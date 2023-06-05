"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from accounts.views import AccountsIndexView, LoginView, RegistrationView, PersonalInformationView, LogoutView, \
    SendOPTView, ConfirmPhoneView, RegistrationConfirmView

urlpatterns = [
    path('', AccountsIndexView.as_view(), name='accounts_index'),
    path('login', LoginView.as_view(), name='accounts_login'),
    path('logout', LogoutView.as_view(), name='accounts_logout'),
    path('registration', RegistrationView.as_view(), name='accounts_registration'),
    path('profile', PersonalInformationView.as_view(), name='accounts_personal_information'),
    path('send_otp', SendOPTView.as_view(), name='accounts_sendotp'),
    path('confirm_phone', ConfirmPhoneView.as_view(), name='accounts_confirm_phone'),
    path("registration/<uidb64>/<token>/", RegistrationConfirmView.as_view(), name="registration_confirm", ),
]

"""
## COMMENTED as source
urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    path(
        "registration/<uidb64>/<token>/",
        RegistrationConfirmView.as_view(),
        name="registration_confirm",
    ),
    path('login/', LoginView.as_view(), name='login'),
    path(
        "password_change/", auth_views.PasswordChangeView.as_view(),
        name="password_change"
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", auth_views.PasswordResetView.as_view(),
         name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]"""
