"""
Модуль содержит `Value Objects` бизнеса (домена).

P.s. Domain Driven Design
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


ID = UUID
USD = Decimal
BTC = Decimal
PnLIndex = Decimal


@dataclass
class Period:
    """
    :param start: Начало периода.
    :param end: Конец периода.
    """
    start: datetime
    end: datetime


@dataclass
class Calculation:
    """
    :param datetime_: Дата и время курса.
    :param btc_rate: Курс BTC.
    :param net_assets: Чистые активы.
    :param pnl: Profit and Loss.
    :param pnl_index: Profit and Loss Index.
    """
    datetime_: datetime
    btc_rate: USD
    net_assets: USD
    pnl: USD
    pnl_index: PnLIndex
