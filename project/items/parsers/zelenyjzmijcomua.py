from .parser import AbstractItemParser
from bs4 import BeautifulSoup
from items.models import Item

class ZelenyjZmij(AbstractItemParser):
    def __init__(self):
        super().__init__({
                           'source_id': 'ZZM',
                           'source_name': 'zelenyjzmij',
                           'is_price_included': True,
                           'is_active': True,
                           'url': 'https://zelenyjzmij.com.ua/',
                           'dataurl': 'https://zelenyjzmij.com.ua/dostavka'
                       })

    def prepare_list_of_items(self):
        html = self.get_html(self.dataurl)
        soup = BeautifulSoup(html)
        cards_list = soup.find_all('div', class_='t-item')
        for card in cards_list:
            try:
                item = Item()
                item.url = ''
                self.set_item_sku(item=item, sku=card.get('data-product-lid'))
                item.caption = card.find('div', class_='t-name').text
                item.description = card.find('div', class_='t-descr').text
                item.img_url = card.find('div', class_='t-bgimg').get('data-original')
                item.is_active = self.is_active
                if self.is_price_included:
                    price = ''.join(c for c in card.find('div', class_='js-product-price').text if c.isdigit())
                    item.price = price
                else:
                    item.price = 0
            except (AttributeError):
                continue

            self._list_of_items.append(item)

    def enrich_item_lazy(self, item):
        if not item.img_url:
            return False
        self.set_item_image_from_url(item=item, url=item.img_url)
        return True

