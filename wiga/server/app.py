__all__ = ["App"]

import asyncio
import logging
import typing as ty
from enum import Enum

from wiga import Message
from wiga.core.background import Backgroundable

from .listeners import Listener

HANDLER = ty.Callable[[Message], ty.Awaitable]
logger = logging.getLogger(__name__)


class App(Backgroundable):
    task_names = ("run",)

    def __init__(self):
        super().__init__()
        self.listeners: set[Listener] = set()
        self.handler_by_topic: dict[Enum, HANDLER] = {}
        self.incoming_messages = asyncio.Queue()

    def add_listener(self, listener: Listener):
        listener.incoming_messages = self.incoming_messages
        self.listeners.add(listener)

    def add_handler(self, topic: Enum, handler: HANDLER):
        self.handler_by_topic[topic] = handler

    async def run(self):
        try:
            for listener in self.listeners:
                await listener.start()
            while True:
                message: Message = await self.incoming_messages.get()
                handler = self.handler_by_topic.get(message.topic, None)
                if handler is not None:
                    await handler(message)
        except Exception as e:
            logger.exception("Exception occurred:", exc_info=e)
            raise
        finally:
            for listener in self.listeners:
                await listener.stop()
