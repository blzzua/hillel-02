import logging

from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager as OrigAuthUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from django.core.cache import caches
otp_storage = caches['otp']


class UserManager(OrigAuthUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)
    first_name = models.CharField(verbose_name="first name", max_length=150, blank=True)
    last_name = models.CharField(verbose_name="last name", max_length=150, blank=True)
    is_staff = models.BooleanField("staff status", default=False,
                                   help_text="Designates whether the user can log into this admin site.", )
    is_active = models.BooleanField(verbose_name="active",
                                    default=True,
                                    help_text="Designates whether this user should be treated as active. "
                                              "Unselect this instead of deleting accounts.",
                                    )
    date_joined = models.DateTimeField(verbose_name="date joined", default=timezone.now)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_phone_valid = models.BooleanField(default=False)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def check_optpassword(self, password):
        if self.phone and password:
            logging.warning(f' check otppassword correct={otp_storage.get(key=self.phone)}, test={password}')
            return password == otp_storage.get(key=self.phone)
        else:
            return False
