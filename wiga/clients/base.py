__all__ = ["Client"]

import asyncio
import logging
import typing as ty
from abc import (
    ABC,
    abstractmethod,
)
from enum import Enum

from wiga import (
    Codec,
    Message,
)
from wiga.core.background import Backgroundable

HANDLER = ty.Callable[[Message], ty.Awaitable]
logger = logging.getLogger(__name__)


class Client(Backgroundable, ABC):
    def __init__(
        self,
        codec: Codec,
    ):
        super().__init__()
        self.codec = codec
        self.handler_by_topic: dict[Enum, HANDLER] = {}
        self.messages = asyncio.Queue()

    @abstractmethod
    async def send(self, message: Message):
        pass

    def add_handler(self, topic: Enum, handler: HANDLER):
        self.handler_by_topic[topic] = handler

    async def run(self):
        while True:
            message: Message = await self.messages.get()
            handler = self.handler_by_topic.get(message.topic, None)
            if handler is not None:
                await handler(message)
