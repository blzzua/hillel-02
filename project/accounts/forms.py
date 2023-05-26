import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import models, Form, CharField, TextInput, PasswordInput, NumberInput


User = get_user_model()


def phone_normalize(phone_num):
    phone_regex = re.match(r'^\+?(?:38)?(0\d{9})$', phone_num.strip())
    if bool(phone_regex):
        # valid phone number formated as 380991234567
        return '38'+phone_regex.groups()[0]


class LoginForm(Form):
    email = CharField(label='email or phone', widget=TextInput(attrs={"autofocus": True}))
    password = CharField(label='Password', widget=PasswordInput(attrs={"type": "password"}), required=False)
    otp_password = CharField(label='SMS code', widget=NumberInput(attrs={}), required=False)

    def clean_email(self):
        email = self.data.get('email')
        normalized_phone_number = phone_normalize(email)
        if normalized_phone_number:
            return normalized_phone_number
        else:
            return email

    def clean_password(self):
        password = self.data.get('password')
        if password is None:
            return ''
        else:
            return password

    def clean(self):
        password = self.cleaned_data.get('password')
        otp_password = self.cleaned_data.get('otp_password')
        if password:
            self.cleaned_data['password'] = password
        elif otp_password:
            self.cleaned_data['password'] = otp_password
        else:
            self.add_error('password', 'Empty Password (and OTP)')
            self.add_error('otp_password', 'Empty OTP (and Password)')
            # raise ValidationError('Empty Password and OTP')
        return self.cleaned_data


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        print(self)
        user.email = self.cleaned_data.get('email').split('@')[0]
        user.save()
        return user


class PersonalInformationForm(models.ModelForm):
    class Meta:
        model = User
        exclude = ['password']


class OtpForm(Form):
    phone_number = CharField()

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        normalized_phone_number = phone_normalize(phone_number)
        if normalized_phone_number:
            return normalized_phone_number


class ConfirmPhoneForm(Form):
    phone_number = CharField(label='Phone number', widget=TextInput(attrs={
        'placeholder': '+380991234567',
        'title': 'phone number  (+380991234567, 380991234567, 0991234567)',
        'pattern': r'^\+?(?:38)?0\d{9}$',
        'tabindex': 1
    }))
    otp = CharField(label='SMS code', widget=TextInput(attrs={
        'placeholder': '',
        'pattern': r'^\d{4}$',
        'class': 'no-spinners no-arrows',
        'disabled': True,
        'tabindex': 3
    }))

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        normalized_phone_number = phone_normalize(phone_number)
        if normalized_phone_number:
            return normalized_phone_number

    def clean_otp(self):
        otp = self.data.get('otp')
        # TODO: implement otp validation respectable max otp len
        return otp
