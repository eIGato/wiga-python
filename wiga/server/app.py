__all__ = ["App"]

import asyncio
import typing as ty
from enum import Enum

from wiga import Message
from wiga.core.background import Backgroundable

from .listeners import Listener

HANDLER = ty.Callable[[Message], ty.Awaitable]


class App(Backgroundable):
    def __init__(self):
        super().__init__()
        self.listeners: set[Listener] = set()
        self.handler_by_topic: dict[Enum, HANDLER] = {}
        self.messages = asyncio.Queue()

    def add_listener(self, listener: Listener):
        listener.messages = self.messages
        self.listeners.add(listener)

    def add_handler(self, topic: Enum, handler: HANDLER):
        self.handler_by_topic[topic] = handler

    async def run(self):
        for listener in self.listeners:
            await listener.start()
        try:
            while True:
                message: Message = await self.messages.get()
                handler = self.handler_by_topic.get(message.topic, None)
                if handler is not None:
                    await handler(message)
        finally:
            for listener in self.listeners:
                await listener.start()
