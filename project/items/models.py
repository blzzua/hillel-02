import uuid

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.db import models
from os import path

from django.utils.safestring import mark_safe
from currencies.models import Currency
from decimal import Decimal
from django.utils.functional import cached_property


User = get_user_model()
MIN_PRICE = 0.1


def upload_to(instance, filename):
    _name, extenstion = path.splitext(filename)
    return str(f'products/images/{str(instance.pk)}{extenstion}')


class Category(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, upload_to=upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def get_categories_names(self):
        return self.name

    def __str__(self):
        return f'{self.name}'

    def img_preview(self):
        if self.image:
            return mark_safe(f'<img src = "{self.image.url}" width = "120"/>')
        else:
            return mark_safe('<b>NO IMAGE</b>')


class Item(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4)
    caption = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, upload_to=upload_to)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    sku = models.CharField(max_length=128)
    categories = models.ManyToManyField(Category, related_name='category', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.caption} [{self.sku}]'

    def img_preview(self):
        if self.image:
            return mark_safe(f'<img src = "{self.image.url}" width = "120"/>')
        else:
            return mark_safe('<b>NO IMAGE</b>')

    img_preview.short_description = 'Image'
    img_preview.allow_tags = True

    def _price_as_CCY(self, ccy_code):
        cache = caches['ccy']
        ccy = cache.get(ccy_code)
        if not ccy:
            ccy = Currency.objects.get(code=ccy_code)
            cache.set(ccy_code, ccy)
        return Decimal(self.price / ccy.amount)

    @property
    def price_as_DOGE(self):
        return Decimal(self._price_as_CCY(ccy_code='DOGE'))

    @property
    def price_as_UAH(self):
        return round(self._price_as_CCY(ccy_code='UAH'), 5)

    @property
    def price_as_USD(self):
        return round(self._price_as_CCY(ccy_code='USD'), 5)

    @property
    def price_as_EUR(self):
        return round(self._price_as_CCY(ccy_code='EUR'), 5)


class Discount(models.Model):
    class DiscountType(models.IntegerChoices):
        PCT = 0, 'percentage'
        ABS = 1, 'absolute'

    code = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)
    discount_type = models.PositiveSmallIntegerField(choices=DiscountType.choices, default=DiscountType.ABS)
    amount = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
