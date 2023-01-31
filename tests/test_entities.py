from datetime import datetime
from unittest import TestCase

from domain.entities import Account
from domain.value_objects import USD, Calculation, BTC, PnLIndex


class TakeRateTest(TestCase):

    def setUp(self) -> None:
        self.account = Account(
            id_='',
            balance=BTC('10'),
            calculations=list(),
        )

    def test_first_day_calculation(self):
        btc_rate=USD('20_000')
        rate_datetime = datetime(2022, 1, 1)
        sample_calculation = Calculation(
            datetime_=rate_datetime,
            btc_rate=btc_rate,
            net_assets=USD('200_000'),
            pnl=USD('0'),
            pnl_index=PnLIndex('1')
        )
        calculation = self.account.take_rate(
            rate=btc_rate, rate_datetime=rate_datetime
        )
        self.assertEqual(sample_calculation, calculation)

    def test_second_day_calculation(self):
        self.account.calculations.append(
            Calculation(
                datetime_=datetime(2022, 1, 1),
                btc_rate=USD('20_000'),
                net_assets=USD('200_000'),
                pnl=USD('0'),
                pnl_index=PnLIndex('1')
            )
        )
        btc_rate = USD('25_000')
        rate_datetime = datetime(2022, 1, 2)
        sample_calculation = Calculation(
            datetime_=rate_datetime,
            btc_rate=btc_rate,
            net_assets=USD('250_000'),
            pnl=USD('50_000'),
            pnl_index=PnLIndex('1.25')
        )
        calculation = self.account.take_rate(
            rate=btc_rate, rate_datetime=rate_datetime
        )
        self.assertEqual(sample_calculation, calculation)
