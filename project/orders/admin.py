from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem
admin.site.register(Order)


@admin.register(OrderItem)
class AdminOrderItem(admin.ModelAdmin):
    pass
