import logging
from django.db.models.signals import post_save, post_delete, pre_save
from orders.models import Order, OrderItem
from items.models import Discount
from django.dispatch import receiver
from decimal import Decimal


@receiver(pre_save, sender=Order)
def pre_save_order_signal(*args, **kwargs):
    logging.warning(f'pre_save_order_signal: {args} {kwargs}')
    # calculate_total_price()


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def post_save_orderitem_signal(*args, **kwargs):
    orderitem = kwargs.get('instance')
    order = orderitem.order_id
    total_amount = 0
    for order_item in order.order_items.iterator():
        total_amount += order_item.amount
    order.total_amount = total_amount
    order.save()


@receiver(pre_save, sender=OrderItem)
def pre_save_discount_orderitem_signal(*args, **kwargs):
    orderitem = kwargs.get('instance')
    orderitem.amount = int(orderitem.quantity) * orderitem.item_price

    def calculate_discount_amount(orderitem):
        discount = orderitem.discount_id
        if discount is None or not discount.is_active:
            return 0
        else:
            if discount.discount_type == Discount.DiscountType.ABS.value:
                return discount.amount
            elif discount.discount_type == Discount.DiscountType.PCT.value:
                return Decimal(orderitem.amount) * (Decimal(discount.amount) / 100)

    orderitem.discount_amount = calculate_discount_amount(orderitem)
    orderitem.amount -= orderitem.discount_amount
    # orderitem.save()  avoid recurstion.
    OrderItem.objects.filter(id=orderitem.id).update(
        amount=orderitem.amount,
        discount_amount=orderitem.discount_amount,
    )
