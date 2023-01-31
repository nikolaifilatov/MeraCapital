"""
Основным смысловым содержанем модуля являются сценарии бизнеса (домена).

P.s. Domain Driven Design
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.value_objects import USD, ID, Period, PnLIndex
from domain.services import AccountStorage


class Command(ABC):
    """Абстрактный класс команды (CQRS)."""


class Query(ABC):
    """Абстрактный класс запроса (CQRS)."""


class QueryResult(ABC):
    """Абстрактный класс результата на запрос (CQRS)."""


class CommandHandler(ABC):
    """Абстрактный класс обработчика команды (CQRS)."""

    @abstractmethod
    def execute(self, command: Command) -> None:
        """Метод выполнения логики обработчика команды, соответствующей ему.

        :param command: Реализация команды.
        :return:
        """


class QueryHandler(ABC):
    """Абстрактный класс обработчика запроса (CQRS)."""

    @abstractmethod
    def execute(self, query: Query) -> QueryResult:
        """Метод выполнения логики обработчика запроса, соответствующего ему.

        :param query: Реализация запроса.
        :return: Результат работы обработчика.
        """


@dataclass
class MakePnLCalculation(Command):
    """Комманда выполнения расчета PnL.

    :param rate: Курс валюты.
    :param currency_datetime: Дата и время курса валюты.
    :return:
    """
    rate: USD
    currency_datetime: datetime


class MakePnLCalculationHandler(CommandHandler):
    """Обработчик комманды выполнения расчета PnL."""

    def __init__(self, storage: AccountStorage) -> None:
        """
        :param storage: Хранилище аккаунтов.
        :return:
        """
        self._storage = storage

    def execute(self, command: MakePnLCalculation) -> None:
        account = self._storage.get()
        account.take_rate(
            rate=command.rate,
            rate_datetime=command.currency_datetime
        )
        self._storage.save(account)


@dataclass
class GetPnLForPeriod(Query):
    """Запрос на получение расчетов за определенный период.

    :param period: Период, за который нужно получить расчеты.
    :return:
    """
    period: Optional[Period] = None


@dataclass
class GetPnLForPeriodResult(QueryResult):
    """Запрос на получение расчетов за определенный период.

    :param account_balance: Текущий баланс аккаунта.
    :param pnl: PnL за период.
    :param pnl_percentage: PnL за период, в процентах.
    :param pnl_index: Индекс PnL за период.
    :param period: Период, за который произведен расчет PnL.
    :return:
    """
    account_balance: USD
    pnl: USD
    pnl_percentage: str
    pnl_index: PnLIndex
    period: Period


class GetPnLForPeriodHandler(QueryHandler):
    """Обработчик запроса на получение расчетов за определенный период."""

    def __init__(self, storage: AccountStorage) -> None:
        """
        :param storage: Хранилище аккаунтов.
        :return:
        """
        self._storage = storage

    def execute(self, query: GetPnLForPeriod) -> GetPnLForPeriodResult:
        account = self._storage.get()
        if not account:
            return
        if query.period is None:
            period_calculates = account.calculations
        else:
            period_calculates = [
                calculate for calculate in account.calculations
                if query.period.start <= calculate.datetime_ <= query.period.end
            ]
        if not period_calculates:
            _now = datetime.now()
            return GetPnLForPeriodResult(
                account_balance=account.balance,
                pnl=USD('0'),
                pnl_percentage='0%',
                pnl_index=PnLIndex('1'),
                period=Period(_now, _now),
            )

        start = min(period_calculates, key=lambda c: c.datetime_)
        end = max(period_calculates, key=lambda c: c.datetime_)
        return GetPnLForPeriodResult(
            account_balance=account.balance,
            pnl=end.net_assets - start.net_assets,
            pnl_percentage=f'{end.net_assets / start.net_assets - 1:.0%}',
            pnl_index=end.net_assets / start.net_assets * start.pnl_index,
            period=Period(start=start.datetime_, end=end.datetime_)
        )
