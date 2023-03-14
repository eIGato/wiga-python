__all__ = ["Codec"]

from abc import (
    ABC,
    abstractmethod,
)

from wiga.message import Message


class Codec(ABC):
    @abstractmethod
    def encode(self, message: Message) -> bytes:
        pass

    @abstractmethod
    def decode(self, raw_message: bytes) -> Message:
        pass
