import logging
import os
from io import BytesIO
import json
from bs4 import BeautifulSoup
import requests
from django.core.files.images import ImageFile
from items.models import Item


class AbstractItemParser():
    def __init__(self, item_parser_source):
        """item_parser_source = {
        'source_id': 'FAW',                              # source mnemonic identidicator
        'source_name': 'foodandwine',                    # source long name
        'is_price_included': False,                      # flag, is price exists in source. default False.
        'is_active': False,                              # flag, is all items will be active. False for items without price.
        'url': 'https://www.foodandwine.com/',           # title source url
        'dataurl': 'https://www.foodandwine.com/recipes' # url source of list items
    }"""
        self._list_of_items = []
        self._index = 0
        for key, value in item_parser_source.items():
            setattr(self, key, value)
        self.prepare_list_of_items()


    def prepare_list_of_items(self):
        """create items list inside of class instance"""
        raise NotImplementedError

    def enrich_item_lazy(self, item):
        """deferred item processing, like download images.
        called in self.__next__() after prepare_list_of_items"""
        raise NotImplementedError

    def set_item_sku(self, item: Item, sku: str):
        """sku format from source ID and source SKU"""
        item.sku = f"{self.source_id}:{sku}"

    def get_html(self, url, *args, **kwargs):
        """helper"""
        if 'headers' in kwargs:
            headers = kwargs.get('headers')
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'uk,en-US;q=0.7,en;q=0.3',
                'Connection': 'keep-alive',
            }
        r = requests.get(url=url, headers=headers)
        if r.ok:
            return r.text
        else:
            return ''

    def set_item_image_from_url(self, item, url, *args, **kwargs):
        """helper for save image from url"""
        filename = os.path.basename(url)
        if 'headers' in kwargs:
            headers = kwargs.get('headers')
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'uk,en-US;q=0.7,en;q=0.3',
                'Connection': 'keep-alive',
            }
        try:
            r = requests.get(url=url, headers=headers)
            if r.status_code == 200:
                image_data = ImageFile(BytesIO(r.content), name=filename)
                item.image = image_data
                return True
            else:
                return False
        except:
            return False


    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._list_of_items):
            current_item = self._list_of_items[self._index]
            self._index += 1
            self.enrich_item_lazy(item=current_item)
            return current_item
        else:
            raise StopIteration
