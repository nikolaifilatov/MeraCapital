import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Process
from time import sleep
from typing import List
from threading import Thread

from domain.value_objects import USD
from usecases import MakePnLCalculation, MakePnLCalculationHandler
from .http_client import HttpClient


logger = logging.getLogger('test_task.jobs')


class Job(ABC):
    def __init__(self, repeat_each: int):
        self.repeat_each = repeat_each

    @abstractmethod
    def do(self) -> None:
        pass


class JobDispatcher(ABC):
    def __init__(self, jobs: List[Job]) -> None:
        self._jobs = jobs
        self._job_tasks: List[asyncio.Task] = list()

    @abstractmethod
    def run(self) -> None:
        pass


class SimpleJobDispatcher(JobDispatcher):
    def run(self) -> None:
        for job in self._jobs:
            self._job_tasks.append(
                Process(target=self._run_job, args=(job,)).start()
            )

    @staticmethod
    def _run_job(job: Job) -> None:
        while True:
            Thread(target=job.do).start()
            sleep(job.repeat_each)


class DeribitCurrencyMonitor(Job):
    
    def __init__(self,
                 http_client: HttpClient,
                 command_resolver: 'Resolver',
                 repeat_each: int):
        super().__init__(repeat_each=repeat_each)
        self._http_client = http_client
        self._command_resolver = command_resolver

    def do(self) -> None:
        logger.info('Job %s has been started...', self.__class__.__name__)
        result = asyncio.run(self._http_client.get(
            'https://test.deribit.com/'
            'api/v2/public/get_last_trades_by_currency'
            '?count=1'
            '&currency=BTC'
        ))
        command = MakePnLCalculation(
            currency_datetime=datetime.now(),
            rate=USD(result['result']['trades'][0]['price'])
        )
        logger.debug('Command completed: %s', command)
        command_handler = self._command_resolver.resolve(command)
        logger.info(
            'Parced command and its handler: %s => %s',
            command.__class__.__name__,
            command_handler.__class__.__name__,
        )
        command_handler.execute(command)
