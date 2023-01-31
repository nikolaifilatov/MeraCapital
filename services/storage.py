import asyncio
import logging
import os
from asgiref.sync import sync_to_async
from typing import List, Optional

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'services.django_orm_settings')
import django
django.setup()

from django.db.transaction import atomic

from domain.entities import Account
from domain.services import AccountStorage
from domain.value_objects import BTC, Calculation, ID
from .http_client import HttpClient
from .orm.models import Account as AccountModel, Calculation as CalculationModel


logger = logging.getLogger('test_task.services.storage')

DERIBIT_API_PATH = 'https://test.deribit.com/api/v2/'


class DjangoOrmAccountStorage(AccountStorage):

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        if not AccountModel.objects.exists():
            AccountModel.objects.create(account_id='test')
        self._client_id = os.environ.get('DEREBIT_CLIENT_ID')
        self._client_secret = os.environ.get('DEREBIT_CLIENT_SECRET')
        if not all((self._client_id, self._client_secret)):
            raise RuntimeError('You must to pass DEREBIT_CLIENT_ID and DEREBIT_CLIENT_SECRET')

    @atomic
    def save(self, account: Account) -> None:
        exist_calculations = CalculationModel.objects.count()
        if exist_calculations == 0:
            exist_calculations = 1
        logger.debug('exist_calculations is %d', exist_calculations)
        to_save = sorted(account.calculations, key=lambda c: c.datetime_)
        to_save = to_save[exist_calculations - len(account.calculations):]
        logger.debug('to_save is %s', to_save)
        if to_save:
            logger.info(
                'Saving new calculations (%d items) for account %s',
                len(to_save), account.id_
            )
        CalculationModel.objects.bulk_create([self._to_model(vo) for vo in to_save])

    def get(self) -> Account:
        account = AccountModel.objects.prefetch_related('calculation_set').first()
        account = self._to_entity(account)
        logger.debug('Got account: %s', account)
        return account

    def _get_account_balance(self) -> BTC:
        response = asyncio.run(self._http_client.get(
            DERIBIT_API_PATH
            + f'public/auth'
              f'?client_id={self._client_id}'
              f'&client_secret={self._client_secret}'
              f'&grant_type=client_credentials'
        ))

        response = asyncio.run(self._http_client.get(
            DERIBIT_API_PATH
            + 'private/get_account_summary'
              '?currency=BTC',
            headers={
                'Authorization': 'Bearer ' + response['result']['access_token']
            }
        ))
        account_balance = response['result']['available_funds']
        logger.debug('Getting account balance result: %s', account_balance)
        return BTC(str(account_balance))

    @staticmethod
    def _to_model(calculation: CalculationModel) -> Calculation:
        return CalculationModel(
            account_id_id='test',
            date_time=calculation.datetime_,
            btc_rate=calculation.btc_rate,
            net_assets=calculation.net_assets,
            pnl=calculation.pnl,
            pnl_index=calculation.pnl_index
        )

    def _to_entity(self, model: AccountModel) -> Account:
        calculations = [
            Calculation(datetime_=calculation.date_time,
                        btc_rate=calculation.btc_rate,
                        net_assets=calculation.net_assets,
                        pnl=calculation.pnl,
                        pnl_index=calculation.pnl_index)
            for calculation in model.calculation_set.all()
        ]
        return Account(
            id_=model.account_id,
            balance=self._get_account_balance(),
            calculations=calculations
        )
