import logging

from currencies.models import Currency
from currencies.clients.api_base_client import APIBaseClient
from decimal import Decimal


class DogePrice(APIBaseClient):
    base_url = 'https://btc-trade.com.ua/api/ticker/doge_uah'

    def _prepare_data(self) -> None:
        """
            {
              "doge_uah": {
                "sell": "3.0678000000",
                "currency_trade": "DOGE",
                "buy_usd": "0.0795288053",
                "buy": "3.0220946000",
                "last": "3.0767600000",
                "updated": 1683023821,
                "vol": "635.7336938900",
                "sell_usd": "0.0807315789",
                "last_usd": "0.0809673684",
                "currency_base": "UAH",
                "vol_cur": "1956.0000000129",
                "high": "3.0767600000",
                "low": "3.0767600000",
                "vol_cur_usd": "51.4736842109",
                "avg": "0.0809673684",
                "usd_rate": "38",
                "last_id": "7441093.0000000000"
              }
            }

        :return: int
        """
        self._request('get')
        logging.info(f'Gathering from btc-trade.com.ua - {self.response.status_code}')
        if self.response.status_code == 200:
            response_object = self.response.json()
            sell = Decimal(response_object.get('doge_uah').get('sell'))
            buy = Decimal(response_object.get('doge_uah').get('buy'))
            self.cross = (sell + buy) / 2

        else:
            logging.error(f'Error on access to btc-trade.com.ua: {self.response.status_code}')
            raise ValueError(f'Wrong response {self.response.json()}')

    def save(self):
        try:
            COIN_DOGE = Currency.objects.get(code='DOGE')
            self._prepare_data()
            amount = COIN_DOGE.amount * self.cross  # COINs in UAH

            Currency.objects.update_or_create(code='UAH', defaults={'amount': amount, 'units': 1})
        except (ValueError, ) as e:
            logging.error(f'error on parsing response {e}')


doge_in_uah_client = DogePrice()
