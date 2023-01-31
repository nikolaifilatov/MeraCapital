import logging
import os
from typing import Union
from threading import Thread

from dotenv import load_dotenv

from services.http_client import SimpleHttpClient
from services.jobs import SimpleJobDispatcher, DeribitCurrencyMonitor
from services.storage import DjangoOrmAccountStorage
from usecases import (Command, CommandHandler,
                      Query, QueryHandler,
                      MakePnLCalculation, MakePnLCalculationHandler,
                      GetPnLForPeriod, GetPnLForPeriodHandler)


load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'WARNING'))
)


class Resolver:

    def __init__(self, map_: dict) -> None:
        self._map = map_

    def resolve(
        self, command_or_query: Union[Command, Query]
    ) -> Union[CommandHandler, QueryHandler]:

        command_or_query_type = type(command_or_query)
        if command_or_query_type not in self._map:
            return
        return self._map[command_or_query_type]


def get_resolver() -> Resolver:
    http_client = SimpleHttpClient()
    account_storage = DjangoOrmAccountStorage(http_client)
    return Resolver(
        {MakePnLCalculation: MakePnLCalculationHandler(account_storage),
         GetPnLForPeriod: GetPnLForPeriodHandler(account_storage)}
    )


def start_jobs() -> None:
    SimpleJobDispatcher(
        jobs=[
            DeribitCurrencyMonitor(
                http_client=SimpleHttpClient(),
                command_resolver=get_resolver(),
                repeat_each=10
            )
        ]
    ).run()


if __name__ == '__main__':
    start_jobs()
