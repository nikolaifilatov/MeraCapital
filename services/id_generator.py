import os

from domain.services import IdGenerator
from domain.value_objects import ID


class UUID4Generator(IdGenerator):

    def generate(self) -> ID:
        return ID(bytes=os.urandom(16), version=4)
