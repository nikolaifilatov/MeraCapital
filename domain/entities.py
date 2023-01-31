"""
Модуль содержит агрегаты бизнеса (домена).

P.s. Domain Driven Design
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List

from .value_objects import ID, BTC, Calculation, USD, PnLIndex


@dataclass
class Account:
    """Представление аккаунта пользователя.

    :param id_: Уникальный идентификатор.
    :param balance: Баланс аккаунта.
    :param calculations: Коллекция проведенных вычислений.
    """
    id_: ID
    balance: BTC
    calculations: List[Calculation]

    def take_rate(self, rate: USD, rate_datetime: datetime) -> Calculation:
        """Производит вычисление на основании переданных параметров
        и добавляет это вычисление в коллекцию вычислений аккаунта.

        :param rate: Курс валюты.
        :param rate_datetime: Дата и время курса валюты.
        :return: Вычисленные параметры.
        """
        net_assets = self.balance * rate
        if len(self.calculations) == 0:
            pnl=USD('0')
            pnl_index=PnLIndex('1.0')
        else:
            first_calculation = min(
                self.calculations,
                key=lambda calculation: calculation.datetime_
            )
            pnl = net_assets - first_calculation.net_assets
            pnl_index = net_assets / (first_calculation.net_assets
                                      * first_calculation.pnl_index)

        calculation = Calculation(
            datetime_=rate_datetime,
            btc_rate=rate,
            net_assets=net_assets,
            pnl=pnl,
            pnl_index=pnl_index
        )
        self.calculations.append(calculation)
        return calculation
