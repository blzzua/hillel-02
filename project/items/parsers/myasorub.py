from .parser import AbstractItemParser
import json
from items.models import Item

class MyasorubParser(AbstractItemParser):
    def __init__(self):
        super().__init__({
            'source_id': 'MRB',
            'source_name': 'myasorub',
            'is_price_included': False,
            'is_active': True,
            'url': 'https://myasorub.if.ua/',
            'dataurl': 'https://store.tildacdn.com/api/getproductslist/?storepartuid=349572444851&recid=325946910&getparts=false&getoptions=false&size=99'
        })

    def prepare_list_of_items(self):
        content = self.get_html(self.dataurl)
        data = json.loads(content)
        for card in data['products']:
            item = Item()
            item.url = card.get('url')
            self.set_item_sku(item=item, sku=card.get('uid'))
            item.caption = card.get('title')
            item.is_active = self.is_active
            item.price = card.get('price')
            item.img_urls = [subitem['img'] for subitem in json.loads(card.get('gallery')) if 'img' in subitem]  # todo catch json parsing errors.
            # todo: make m2m link on group:       card["partuids"]: "[333865417361]",     data["parts"]: [    { "uid": 333865417361, "title": "Шашлик", "recordid": 0, "sort": 200, "hideonpublic": "" },.. ]
            self._list_of_items.append(item)

    def enrich_item_lazy(self, item):
        if item.img_urls:
            img_url = item.img_urls[0]
            self.set_item_image_from_url(item=item, url=img_url)
            return True
        else:
            return False
