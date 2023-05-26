from django.db.models import TextChoices


class Currencies(TextChoices):
    COIN = 'COIN', 'Valheim gold coin'
    DOGE = 'DOGE', 'Dogecoin'
    UAH = 'UAH', 'UAH'
    USD = 'USD', 'USD'
    EUR = 'EUR', 'EUR'
