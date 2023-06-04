import hashlib
from .parser import AbstractItemParser
from bs4 import BeautifulSoup
from items.models import Item

class ZarabuduParser(AbstractItemParser):
    def __init__(self):
        super().__init__({
                           'source_id': 'ZBD',
                           'source_name': 'zarabudu',
                           'is_price_included': True,
                           'is_active': True,
                           'url': 'https://zarabudu.com.ua/',items/parsers/parser.py
                           'dataurl': 'https://zarabudu.com.ua/product-category/stravy-churrasco/'
                       })

    def prepare_list_of_items(self):
        html = self.get_html(self.dataurl)
        soup = BeautifulSoup(html)
        cards_container = soup.find('div', class_="product-wrapps izotope-block")
        cards_list = cards_container.find_all('div', class_="grid-item")
        for outer_card in cards_list:
            card = outer_card.find('div', class_='product-data')
            item = Item()
            item.url = card.find('div', class_='product-item-top').find('a').get('href')
            item.caption = card.get('data-name')
            item.description = card.find('div', class_='simple-text product-ingredient').find('p').text
            sku = str(int(hashlib.md5(item.url.encode('utf-8')).hexdigest(), 16) % (2 ** 32))
            self.set_item_sku(item=item, sku=sku)
            item.is_active = self.is_active
            if self.is_price_included:
                item.price = card.get('data-current-price')
            else:
                item.price = 0
            item.img_url = card.find('span', class_='product-item-img').find('span', class_='bg').get('data-bg')

            self._list_of_items.append(item)

    def enrich_item_lazy(self, item):
        self.set_item_image_from_url(item=item, url=item.img_url)
        return True

