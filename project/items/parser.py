import os
from io import BytesIO

from bs4 import BeautifulSoup
import requests
from django.core.files.images import ImageFile
from items.models import Item

item_parser_sources = [
    {
        'source_id': 'FAW',
        'source_name': 'foodandwine',
        'is_price_included': False,
        'is_active': False,
        'url': 'https://www.foodandwine.com/recipes'
    },
]


def get_html(url):
    r = requests.get(url=url)
    if r.ok:
        return r.text
    else:
        return ''

def enrich_food_and_wine_picture(item: Item, url: str) :
    card_html = get_html(url)
    soup = BeautifulSoup(card_html)

    # item.description
    description = []
    p1 = soup.find('p', id='article-subheading_1-0')
    p2 = soup.find('p', id='mntl-sc-block_1-0')
    if p1:
        description.append(p1.text.strip('\n'))
    if p2:
        description.append(p2.text.strip('\n'))
    description += [url]
    item.description = '\n'.join(description)
    # end item.description

    img_class = soup.find('img', class_="primary-image__image")
    if not img_class:
        return False
    img_url = img_class.get('src')
    filename = os.path.basename(img_url)
    try:
        r = requests.get(url=img_url)
        if r.status_code == 200:
            image_data = ImageFile(BytesIO(r.content), name=filename)
            item.image = image_data
            return True
        else:
            return False
    except:
        return False
def parse_food_and_wine():
    item_parser_source = {
        'source_id': 'FAW',
        'source_name': 'foodandwine',
        'is_price_included': False,
        'is_active': False,
        'url': 'https://www.foodandwine.com/recipes'
    }
    url = item_parser_source['url']  # todo: validate url as img-url.
    is_active = item_parser_source['is_active']

    html = get_html(url)
    soup = BeautifulSoup(html)
    cards_container = soup.find('div', class_="loc fixedContent")
    cards_list = cards_container.find_all('a', class_="mntl-card-list-items")

    for card in cards_list:
        try:
            url = card.get('href')
            sku = item_parser_source['source_id'] + ':' + card.get('data-doc-id')
            caption = card.find('span', class_='card__title-text').text
            if not item_parser_source['is_active']:
                price = 0
            item, _ = Item.objects.get_or_create(sku=sku, defaults={'caption': caption, 'price': price, 'description': url, 'is_active': is_active})
            if 1 or not item.image:   # TODO: DONE - enrich image only for items without images.
                enrich = enrich_food_and_wine_picture(item=item, url=url)
                if enrich:
                    item.save()
        except ZeroDivisionError as e:
            continue  # skip








