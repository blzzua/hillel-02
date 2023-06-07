import django_filters
from django.utils import timezone
from items.models import Item

class ItemFilter(django_filters.FilterSet):
    caption = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    sku = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.RangeFilter()
    date = django_filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = Item
        fields = ['caption', 'price', 'description']

