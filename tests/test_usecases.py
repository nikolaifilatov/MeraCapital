from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from domain.entities import Account
from domain.value_objects import USD, BTC, Calculation, PnLIndex, Period
from usecases import MakePnLCalculationHandler, MakePnLCalculation, \
    GetPnLForPeriod, GetPnLForPeriodHandler, GetPnLForPeriodResult


class MakePnLCalculationHandlerTest(TestCase):

    def setUp(self):
        self.storage_mock = MagicMock()
        self.command_handler = MakePnLCalculationHandler(self.storage_mock)

    def test_call_account_method(self):
        self.command_handler.execute(
            MakePnLCalculation(
                currency_datetime=datetime(2022, 1, 1),
                rate=USD('20_000')
            )
        )
        self.storage_mock.get().take_rate.assert_called_once()

    def test_save_to_permanent_storage(self):
        self.command_handler.execute(
            MakePnLCalculation(
                currency_datetime=datetime(2022, 1, 1),
                rate=USD('20_000')
            )
        )
        self.storage_mock.save.assert_called_once()


class GetPnLForPeriodTest(TestCase):

    def setUp(self) -> None:
        self.account = Account(
            id_='',
            balance=BTC('10'),
            calculations=[
                Calculation(
                    datetime_=datetime(2022, 1, 1),
                    btc_rate=USD('20_000'),
                    net_assets=USD('200_000'),
                    pnl=USD('0'),
                    pnl_index=PnLIndex('1')
                ),
                Calculation(
                    datetime_=datetime(2022, 1, 2),
                    btc_rate=USD('25_000'),
                    net_assets=USD('250_000'),
                    pnl=USD('50_000'),
                    pnl_index=PnLIndex('1.25')
                ),
                Calculation(
                    datetime_=datetime(2022, 1, 3),
                    btc_rate=USD('23_000'),
                    net_assets=USD('230_000'),
                    pnl=USD('30_000'),
                    pnl_index=PnLIndex('1.15')
                ),
            ],
        )
        self.storage_mock = MagicMock()
        self.storage_mock.get.return_value = self.account
        self.command_handler = GetPnLForPeriodHandler(self.storage_mock)

    def test_some_period(self):
        period = Period(
            start=datetime(2022, 1, 2),
            end=datetime(2022, 1, 3)
        )
        sample_result = GetPnLForPeriodResult(
            account_balance=BTC('10'),
            pnl=USD('-20_000'),
            pnl_percentage='-8%',
            pnl_index=PnLIndex('1.15'),
            period=period,
        )
        result = self.command_handler.execute(
            GetPnLForPeriod(
                period=period
            )
        )
        self.assertEqual(sample_result, result)

    def test_total_period(self):
        period = Period(
            start=datetime(2022, 1, 1),
            end=datetime(2022, 1, 3)
        )
        sample_result = GetPnLForPeriodResult(
            account_balance=BTC('10'),
            pnl=USD('30_000'),
            pnl_percentage='15%',
            pnl_index=PnLIndex('1.15'),
            period=period,
        )
        result = self.command_handler.execute(
            GetPnLForPeriod(
                period=period
            )
        )
        self.assertEqual(sample_result, result)

    @patch('usecases.Period')
    def test_there_are_no_calculations(self, period_stub):
        self.account.calculations = list()
        sample_result = GetPnLForPeriodResult(
            account_balance=BTC('10'),
            pnl=USD('0'),
            pnl_percentage='0%',
            pnl_index=PnLIndex('1'),
            period=period_stub(),
        )
        result = self.command_handler.execute(GetPnLForPeriod())
        self.assertEqual(sample_result, result)
