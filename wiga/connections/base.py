from __future__ import annotations

__all__ = [
    "Connection",
    "IncomingConnection",
    "OutgoingConnection",
]

import asyncio
import logging
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import (
    dataclass,
    field,
)

from wiga import (
    codecs,
    models,
)
from wiga.core import (
    Backgroundable,
    LockableDeque,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class Connection(Backgroundable, ABC):
    codec: codecs.Codec
    incoming_messages: asyncio.Queue[models.Message] = field(
        default_factory=asyncio.Queue,
    )
    # Only for Outgoing:
    incoming_perspectives: LockableDeque = field(
        default_factory=lambda: LockableDeque(maxlen=32),
    )
    # Only for Incoming:
    player: models.Player | None = None
    outgoing_perspectives: LockableDeque = field(
        default_factory=lambda: LockableDeque(maxlen=32),
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"(codec={self.codec}, player={self.player})"
        )

    @abstractmethod
    async def send(self, message: models.Message):
        pass

    async def on_receive(self, data: bytes):
        try:
            message = self.codec.decode(data)
        except Exception:
            logger.warning(f"Got unreadable {data=}")
            return
        message.connection = self
        await self.incoming_messages.put(message)


class IncomingConnection(Connection):
    """Connection that server gets from client."""

    task_names = Connection.task_names + ("process_perspectives",)

    async def send_perspective(self, perspective):
        perspectives = self.outgoing_perspectives
        async with perspectives.lock:
            perspectives.append(perspective)

    async def process_perspectives(self):
        # TODO: Send diffs.
        perspectives = self.outgoing_perspectives
        while True:
            try:
                async with perspectives.lock:
                    perspective = perspectives.popleft()
            except IndexError:
                await asyncio.sleep(0.001)
                continue
            await self.send(
                models.Message(topic=models.Topic.LOBBY, content=perspective)
            )


class OutgoingConnection(Connection, ABC):
    """Connection that client makes to server."""

    task_names = Connection.task_names + ("connect",)

    @abstractmethod
    async def connect(self):
        """Make an outgoing connection."""
        pass
