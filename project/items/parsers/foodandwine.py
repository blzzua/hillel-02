from .parser import AbstractItemParser
from bs4 import BeautifulSoup
from items.models import Item

class FoodAndWineParser(AbstractItemParser):
    def __init__(self):
        super().__init__({
                           'source_id': 'FAW',
                           'source_name': 'foodandwine',
                           'is_price_included': False,
                           'is_active': False,
                           'url': 'https://www.foodandwine.com/',
                           'dataurl': 'https://www.foodandwine.com/recipes'
                       })

    def prepare_list_of_items(self):
        html = self.get_html(self.dataurl)
        soup = BeautifulSoup(html)
        cards_container = soup.find('div', class_="loc fixedContent")
        cards_list = cards_container.find_all('a', class_="mntl-card-list-items")
        for card in cards_list:
            item = Item()
            item.url = card.get('href')
            self.set_item_sku(item=item, sku=card.get('data-doc-id'))
            item.caption = card.find('span', class_='card__title-text').text
            item.is_active = self.is_active
            if self.is_price_included:
                item.price = self.set_item_price()
            else:
                item.price = 0
            self._list_of_items.append(item)

    def enrich_item_lazy(self, item):
        card_html = self.get_html(item.url)
        soup = BeautifulSoup(card_html)
        p1 = soup.find('p', id='article-subheading_1-0')
        p2 = soup.find('p', id='mntl-sc-block_1-0')
        description = [p.text.strip('\n') for p in (p1, p2) if p]
        description += [item.url]
        item.description = '\n'.join(description)

        img_class = soup.find('img', class_="primary-image__image")
        if not img_class:
            return False
        self.set_item_image_from_url(item=item, url=img_class.get('src'))
        return True

