from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, RedirectView, FormView
from django.views.generic.edit import FormMixin
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse, reverse_lazy
from accounts.forms import RegistrationForm, LoginForm, OtpForm, ConfirmPhoneForm
from django.contrib.auth import get_user_model
from project.celery import send_otp
from project.constants import OTP_LENGTH
from random import randint
from django.core.cache import caches
from django.contrib import messages
from .tasks import send_registration_email

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
            user = authenticate(request, email=form.cleaned_data.get('email'),
                                password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                messages.success(request=request, message=f'WELLCOME {user.email} info', extra_tags="HEADER")  # noqa
                messages.info(request=request, message=f'this is info message', extra_tags="HEADER")  # noqa
                messages.debug(request=request, message=f'this is debug message', extra_tags="HEADER")  # noqa
                messages.warning(request=request, message=f'this is warning message', extra_tags="HEADER")  # noqa
                messages.error(request=request, message=f'this is error message', extra_tags="HEADER")  # noqa
                messages.error(request=request,
                               message=f'this is error message but not shown because does not have extratag')  # noqa
                return redirect('accounts_personal_information')
            else:
                messages.error(request=request, message=f'{user}', extra_tags="HEADER")
                form.add_error('password', 'LOGIN FAILED')
                context['form'] = form

        #   request, template_name, context=None, content_type=None, status=None, using=None
        return render(request, template_name=self.get_template_names(), context=context)


class RegistrationView(TemplateView, FormMixin):
    template_name = 'accounts/registration.html'
    get_redirect_url = 'accounts_personal_information'
    form_class = RegistrationForm
    success_url = reverse_lazy('main')
    email_template_name = "accounts/registration_email.html"
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    token_generator = default_token_generator

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            context = {
                "domain": 'shop.com',
                "site_name": 'shop.com',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": self.token_generator.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
                **(self.extra_email_context or {}),
            }
            send_registration_email(
                self.email_template_name,
                context,
                self.from_email,
                user.email,
                self.html_email_template_name
            )
            print(request, 'You have singed up successfully.')
            messages.success(request, 'We will send email with registration link. '
                                      'Please follow link and continue your registration flow.',
                             extra_tags="HEADER")
            # login(request, user)
            return redirect('accounts_personal_information')
        else:
            #   request, template_name, context=None, content_type=None, status=None, using=None
            return render(request=request, template_name=self.template_name)


class RegistrationConfirmView(RedirectView):
    url = reverse_lazy('accounts_login')
    user = None

    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is None:
            raise Http404
        if not default_token_generator.check_token(self.user, kwargs["token"]):
            raise Http404
        self.user.is_active = True
        self.user.save()
        return super().dispatch(*args, **kwargs)

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user


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
