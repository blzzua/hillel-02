from django.db import models
from project.constants import MAX_DIGITS
from project.model_choices import Currencies


class Currency(models.Model):
    code = models.CharField(primary_key=True, max_length=16, choices=Currencies.choices,  default=Currencies.COIN)
    amount = models.DecimalField(max_digits=MAX_DIGITS, decimal_places=8, default=1)
    units = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.amount}"
