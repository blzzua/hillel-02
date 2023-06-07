import django_filters
from django.utils import timezone
from items.models import Item

class ItemFilter(django_filters.FilterSet):
    caption = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['caption']