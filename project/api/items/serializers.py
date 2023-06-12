from rest_framework import serializers

from items.models import Item


class ItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ('id', 'caption', 'price', 'sku', 'created_at', 'updated_at',
                  'description', 'image', 'categories', 'category_name')

    def get_category_name(self, obj):
        return obj.categories.values_list('name', flat=True)