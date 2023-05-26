
from django.urls import path
from orders.views import OrderItemView, OrderDetailView, OrderItemDetailView, OrderItemDeletelView, OrderClearView, OrderConfirmView, OrderClosedDetailView, OrderListView

urlpatterns = [
    path('add', OrderItemView.as_view(), name='add_orderitem'),
    path('list', OrderListView.as_view(), name='order_list'),
    path('detail', OrderDetailView.as_view(), name='order_detail'),
    path('detailclosed/<uuid:order_id>', OrderClosedDetailView.as_view(), name='order_detail_closed'),
    path('item/<uuid:orderitem_id>/detail', OrderItemDetailView.as_view(), name='order_item_detail'),
    path('item/<uuid:orderitem_id>/delete', OrderItemDeletelView.as_view(), name='order_item_delete'),
    path('clear', OrderClearView.as_view(), name='order_clear'),
    path('confirm', OrderConfirmView.as_view(), name='order_confirm'),
]
