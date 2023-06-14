from rest_framework import generics
from rest_framework.permissions import AllowAny

from api.items.serializers import ItemListSerializer
from items.models import Item


class ItemListAPIView(generics.ListAPIView):
    queryset = Item.objects.prefetch_related('categories').all()
    serializer_class = ItemListSerializer
    permission_classes = [AllowAny]


class ItemAPIView(generics.RetrieveAPIView):
    queryset = Item.objects.prefetch_related('categories').all()
    serializer_class = ItemListSerializer
    permission_classes = [AllowAny]
