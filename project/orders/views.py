from django.http import HttpResponseNotFound
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, View, DetailView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch

from items.models import Item
from orders.models import Order, OrderItem

from project.celery import alert_order_task


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderItemView(View):
    def get(self, request):
        # form = OrderCountView()
        user = request.user
        order, is_created = Order.objects.get_or_create(
            user_name=user, is_active=True,
            defaults={'order_number': -1, 'is_active': True, 'is_paid': False, 'is_active': True}
        )
        if is_created:
            prev_order = Order.objects.filter(user_name=user).order_by('-order_number').first()
            if prev_order:
                order.order_number = prev_order.order_number + 1
                order.save()

        try:
            item_id = request.GET.get('item')
            item = Item.objects.get(pk=item_id)
        except ObjectDoesNotExist:
            # redirect 404
            raise Http404(f"Товар {item_id} не знайдено")

        context = {'item': item, 'order': order}
        return render(request, 'order/add.html', context=context)

    def post(self, request):  # feedback_index
        post_data = request.POST
        order_number = post_data.get('order_number')
        quantity = post_data.get('quantity')
        item_id = post_data.get('item')
        item = Item.objects.get(id=item_id)
        user = request.user
        order = Order.objects.get(user_name=user, is_active=True, order_number=order_number)
        order_item = OrderItem.objects.create(
            is_active=True,
            order_id=order,
            item_id=item,
            discount_id=None,
            item_price=item.price,
            quantity=quantity,
            discount_amount=0,
            amount=item.price
        )
        order_item
        return redirect(reverse('order_detail'))


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderDetailView(View):
    # implement buttons in detail.html
    #  TODO /order/clear">Clear Order</button>
    #  TODO /order/confirm">Confirm Order</button>

    def get(self, request):
        user = request.user
        order, is_created = Order.objects.prefetch_related(Prefetch('order_items', queryset=OrderItem.objects.select_related('item_id'))).get_or_create(
            user_name=user, is_active=True,
            defaults={'order_number': 1, 'is_active': True, 'is_paid': False, 'is_active': True}
        )
        if is_created:
            prev_order = Order.objects.filter(user_name=user).order_by('-order_number').first()
            if prev_order:
                order.order_number = prev_order.order_number + 1
                order.save()
            orderitems = []
        else:
            orderitems = order.order_items.all()
        context = {'order': order, 'orderitems': orderitems}
        return render(request, 'order/detail.html', context=context)


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderItemDetailView(DetailView):
    model = OrderItem
    template_name = 'order/orderitem_detail.html'
    context_object_name = 'order_item'

    def get_object(self, queryset=None):
        return OrderItem.objects.get(id=self.kwargs['orderitem_id'])

    # TODO ./project/templates/order/orderitem_detail.html:    <button type="submit" class="btn btn-primary" formaction="#TODO">Confirm Changes Order </button>


class OrderItemDeletelView(View):
    def post(self, request, *args, **kwargs):
        order_item = OrderItem.objects.get(id=self.kwargs['orderitem_id'])
        order_item.delete()
        return redirect(reverse('order_detail'))


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderClearView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.get(user_name=user, is_active=True)
        for order_item in order.order_items.iterator():
            order_item.delete()
        return redirect(reverse('order_detail'))


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderConfirmView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.get(user_name=user, is_active=True)
        order.is_paid = True
        order.is_active = False
        order.save()
        alert_order_task.delay(order_id=order.id)
        return redirect('order_detail_closed', order_id=order.id)


@method_decorator(login_required(login_url=reverse_lazy('accounts_login')), name='dispatch')
class OrderClosedDetailView(View):
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        order = Order.objects.prefetch_related(
            Prefetch('order_items', queryset=OrderItem.objects.select_related('item_id'))
        ).get(id=order_id)
        if request.user == order.user_name or (request.user.is_staff or request.user.is_superuser):
            orderitems = order.order_items.all()
            context = {'order': order, 'orderitems': orderitems}
            return render(request, 'order/detailclosed.html', context=context)
        else:
            return HttpResponseNotFound('This order not belong you')


class OrderListView(ListView):
    model = Order
    template_name = 'order/list.html'

    def get_queryset(self, request):
        queryset = super().get_queryset()
        queryset = queryset.filter(user_name=request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        return self.render_to_response(context)
