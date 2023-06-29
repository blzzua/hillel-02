import uuid

from django.db import models
from django.contrib.auth import get_user_model
from items.models import Item, Discount

from django.core.cache import caches
from currencies.models import Currency
from decimal import Decimal


User = get_user_model()
MIN_PRICE = 0.1


class Order(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # user_name = models.CharField(max_length=255, null=True, on_delete=models.SET_NULL)
    user_name = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    order_number = models.IntegerField()
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_name', 'order_number')

    # def save(self, *args, **kwargs):
    #     # donot  check if
    #     # if OrderItem.objects.filter(order_id=self, updated_at__gte=self.updated_at):
    #     self.total_price = self.calculate_total_price()
    #     super(Order, self).save(*args, **kwargs)

    def _price_as_CCY(self, ccy_code):
        cache = caches['ccy']
        ccy = cache.get(ccy_code)
        if not ccy:
            ccy = Currency.objects.get(code=ccy_code)
            cache.set(ccy_code, ccy)
        return Decimal(self.total_amount / ccy.amount)

    @property
    def total_amount_as_DOGE(self):
        return Decimal(self._price_as_CCY(ccy_code='DOGE'))


    @property
    def total_amount_as_UAH(self):
        return round(self._price_as_CCY(ccy_code='UAH'), 5)

    @property
    def total_amount_as_USD(self):
        return round(self._price_as_CCY(ccy_code='USD'), 5)

    @property
    def total_amount_as_EUR(self):
        return round(self._price_as_CCY(ccy_code='EUR'), 5)



class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=False)
    order_id = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='order_items', )
    item_id = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    discount_id = models.ForeignKey(Discount, on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0)
    item_price = models.DecimalField(max_digits=18, decimal_places=2)
    quantity = models.SmallIntegerField(default=1)  # TODO: add checks, positive > 0.
    amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
