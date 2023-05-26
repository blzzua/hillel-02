from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView, FormView
from django.views.generic.edit import FormMixin
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from accounts.forms import RegistrationForm, LoginForm, OtpForm, ConfirmPhoneForm
from django.contrib.auth import get_user_model
from project.celery import send_otp
from project.constants import OTP_LENGTH
from random import randint
from django.core.cache import caches
from django.contrib import messages

User = get_user_model()
otp_storage = caches['otp']


class LoginView(FormView):
    template_name = 'accounts/login.html'
    get_redirect_url = 'accounts_personal_information'
    form_class = LoginForm

    def post(self, request):
        context = super().get_context_data()
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                messages.success(request=request, message=f'WELLCOME {user.email} info', extra_tags="HEADER")
                messages.info(request=request, message=f'this is info message', extra_tags="HEADER")
                messages.debug(request=request, message=f'this is debug message', extra_tags="HEADER")
                messages.warning(request=request, message=f'this is warning message', extra_tags="HEADER")
                messages.error(request=request, message=f'this is error message', extra_tags="HEADER")
                messages.error(request=request, message=f'this is error message but not shown because does not have extratag')
                return redirect('accounts_personal_information')
            else:
                form.add_error('password', 'LOGIN FAILED')
                context['form'] = form

        #   request, template_name, context=None, content_type=None, status=None, using=None
        return render(request, template_name=self.get_template_names(), context=context)


class RegistrationView(TemplateView, FormMixin):
    template_name = 'accounts/registration.html'
    get_redirect_url = 'accounts_personal_information'
    form_class = RegistrationForm

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(request, 'You have singed up successfully.')
            login(request, user)
            return redirect('accounts_personal_information')
        else:
            #   request, template_name, context=None, content_type=None, status=None, using=None
            return render(request=request, template_name=self.template_name)


class LogoutView(RedirectView):
    def get(self, reqeust, *args, **kwargs):
        logout(reqeust)
        # return super().get(reqeust, *args, **kwargs)
        return redirect(reverse('accounts_index'))


class AccountsIndexView(TemplateView):
    template_name = 'accounts/personal_information.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = {f.name: getattr(self.request.user, f.name, None) for f in User._meta.get_fields()
                           if f.name in ("id", "last_login", "is_superuser", "first_name", "last_name",
                                         "email", "phone", "is_staff", "is_active", "date_joined")}
        return context


class PersonalInformationView(AccountsIndexView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().get(*args, **kwargs)
        else:
            return redirect(reverse('accounts_login'))


class SendOPTView(TemplateView, FormMixin):
    template_name = 'accounts/login.html'
    form_class = OtpForm

    def post(self, request):
        context = super().get_context_data()
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            min_otp = 1
            max_otp = (10 ** OTP_LENGTH) - 1
            otp = str.zfill(str(randint(min_otp, max_otp)), OTP_LENGTH)
            otp_storage.set(key=phone_number, value=otp, timeout=60)
            send_otp.delay(phone_number=phone_number, otp=otp)
        return render(request, template_name=self.get_template_names(), context=context)


class ConfirmPhoneView(TemplateView, FormMixin):
    template_name = 'accounts/confirm_phone.html'
    form_class = ConfirmPhoneForm
    get_redirect_url = 'accounts_personal_information'

    def post(self, request):
        context = super().get_context_data()
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.user
            if otp_storage.get(key=form.cleaned_data['phone_number']) == form.cleaned_data['otp']:
                prev_phone = user.phone
                new_phone = form.cleaned_data['phone_number']
                if prev_phone:
                    messages.success(request=request,
                                     message=f'Your phone number changed from {user.phone} to {new_phone}',
                                     extra_tags="HEADER")
                else:
                    messages.success(request=request,
                                     message=f'Congrats. Your phone number now is {new_phone}',
                                     extra_tags="HEADER")
                user.phone = new_phone
                user.save()
                return redirect(to=self.get_redirect_url)
            else:
                messages.error(request=request,
                               message=f'Wrong SMS code. Check phone number, request new code try again',
                               extra_tags="HEADER")
                form.add_error('otp', 'otp mismatch')
                form.cleaned_data.update({'otp': ''})
                context['form'] = form
                return render(request, template_name=self.get_template_names(), context=context)
        return render(request, template_name=self.get_template_names(), context=context)
