from abc import ABC, abstractmethod

from .entities import Account
from .value_objects import ID


class IdGenerator(ABC):
    @abstractmethod
    def generate(self) -> ID:
        pass


class AccountStorage(ABC):
    @abstractmethod
    def save(self, account: Account) -> None:
        pass

    @abstractmethod
    def get(self) -> Account:
        pass
