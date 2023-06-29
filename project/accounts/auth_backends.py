import logging
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

UserModel = get_user_model()


class EmailModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = kwargs.get(UserModel.USERNAME_FIELD)
        if email is None or password is None:
            return

        try:
            # user = UserModel._default_manager.get_by_natural_key(username)
            try:
                validate_email(email)
                user = UserModel._default_manager.get(email=email)
            except ValidationError:
                return
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None


class PhoneModelBackend(ModelBackend):
    @staticmethod
    def _validate_phonenumber(phone):
        # valid formats:
        # +380501234567
        # 380501234567
        # 0501234567
        return bool(re.match(r'^\+?(?:38)?0\d{9}$', phone))

    # user = UserModel._default_manager.get(phone=username)
    def authenticate(self, request, email=None, password=None, **kwargs):
        logging.warning(f"authentification PhoneModelBackend: email = {email}, pass = {password}")
        phone = email
        if phone is None or password is None:
            logging.warning(f"authentification PhoneModelBackend: {phone=} is None or {password=} is None")
            return
        try:
            logging.warning(f"authentification PhoneModelBackend: _validate_phonenumber(phone)")
            if PhoneModelBackend._validate_phonenumber(phone):
                user = UserModel._default_manager.get(phone=phone, is_phone_valid=True)
            else:
                return None
        except UserModel.DoesNotExist:
            logging.warning(f"authentification PhoneModelBackend: user not exists")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            logging.warning(f"authentification PhoneModelBackend: check_optpassword")
            if user.check_optpassword(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        is_phone_valid = getattr(user, "is_phone_valid", None)
        return is_active and is_phone_valid
