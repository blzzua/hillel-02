from .foodandwine import FoodAndWineParser
from .myasorub import MyasorubParser
from .zarabudu import ZarabuduParser
from .parser import AbstractItemParser
from ..models import Item
def parse(parser: AbstractItemParser):
    for item in parser:
        Item.objects.update_or_create(sku=item.sku,
                                      defaults={'caption': item.caption,
                                                'price': item.price,
                                                'description': item.description,
                                                'is_active': item.is_active,
                                                'image': item.image,
                                                 })

