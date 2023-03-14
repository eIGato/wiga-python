__all__ = ["Connection"]

import asyncio
import logging
from abc import (
    ABC,
    abstractmethod,
)

from wiga import (
    Codec,
    Message,
)
from wiga.core import Backgroundable

logger = logging.getLogger(__name__)


class Connection(Backgroundable, ABC):
    def __init__(
        self,
        messages: asyncio.Queue,
        codec: Codec,
    ):
        super().__init__()
        self.messages = messages
        self.codec = codec

    @abstractmethod
    async def send(self, message: Message):
        pass

    async def on_receive(self, data: bytes):
        try:
            message = self.codec.decode(data)
        except Exception:
            logger.warning(f"Got unreadable {data=}")
            return
        message.metadata["connection"] = self
        await self.messages.put(message)
