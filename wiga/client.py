__all__ = ["Client"]

import asyncio
import logging
import typing as ty
from abc import ABC
from enum import Enum

from wiga import (
    Codec,
    Message,
)
from wiga.connections import Connection
from wiga.core import Backgroundable

HANDLER = ty.Callable[[Message], ty.Awaitable]
logger = logging.getLogger(__name__)


class Client(Backgroundable, ABC):
    connection_class: ty.Type[Connection] = Connection
    incoming_messages: asyncio.Queue[Message]
    task_names = ("run",)

    def __init__(self, codec: Codec, **kwargs):
        super().__init__()
        self.handler_by_topic: dict[Enum, HANDLER] = {}
        self.incoming_messages = messages = asyncio.Queue()
        self.connection = self.connection_class(incoming_messages=messages, codec=codec, **kwargs)

    def send(self, message: Message):
        return self.connection.send(message)

    def add_handler(self, topic: Enum, handler: HANDLER):
        self.handler_by_topic[topic] = handler

    async def run(self):
        await self.connection.start()
        try:
            while True:
                message: Message = await self.incoming_messages.get()
                handler = self.handler_by_topic.get(message.topic, None)
                if handler is not None:
                    await handler(message)
        finally:
            await self.connection.stop()
