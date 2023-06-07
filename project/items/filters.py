import django_filters
from django.db.models import Q, F, Value, Case, When, CharField
from django.utils import timezone
from items.models import Item

class SearchItemFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='custom_filter', label='Query')
    def custom_filter(self, queryset, name, value):
        return queryset.filter(Q(caption__icontains=value) | Q(description__icontains=value)).annotate(
        match=Case(
            When(caption__icontains=value, then=Value(1)),
            default=Value(2),
            output_field=CharField()
        )
    ).order_by('match', 'caption')

    class Meta:
        model = Item
        fields = ['query']