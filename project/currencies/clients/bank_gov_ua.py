import logging

from currencies.models import Currency
from currencies.clients.api_base_client import APIBaseClient
from decimal import Decimal


class NBUData(APIBaseClient):
    base_url = 'https://bank.gov.ua/NBU_Exchange/exchange'

    def _prepare_data(self) -> None:
        """
        [
            {"StartDate":"03.05.2023","TimeSign":"0000","CurrencyCode":"036","CurrencyCodeL":"AUD","Units":1,"Amount":24.5046 },
            ...
        ]
        :return: None, change state self.response_object
        """
        self._request('get', params={'json': ''})
        logging.info(f'Gathering from bank.gov.ua - {self.response.status_code}')
        if self.response.status_code == 200:
            self.response_object = self.response.json()

        else:
            logging.error(f'Error on access to NBU: {self.response.status_code}')
            raise ValueError(f'Wrong response {self.response.json()}')

    def save(self):
        try:
            UAH_COIN = Currency.objects.get(code='UAH').amount
            self._prepare_data()

            for ticker in ['USD', 'EUR']:
                nbu_data = next(filter(lambda x: x.get('CurrencyCodeL') == ticker, self.response_object))
                nbu_amount = Decimal(nbu_data.get('Amount'))
                nbu_units = Decimal(nbu_data.get('Units'))
                cross_coin_amount = nbu_amount * UAH_COIN
                Currency.objects.update_or_create(
                    code=ticker,
                    defaults={'amount': cross_coin_amount, 'units': nbu_units}
                )
        except (ValueError, ) as e:
            logging.error(f'error on parsing response {e}')


world_ccy_to_uah_client = NBUData()
