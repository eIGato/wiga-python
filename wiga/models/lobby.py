from __future__ import annotations

__all__ = [
    "Lobby",
    "Phase",
]

import asyncio
import logging
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
)
from enum import Enum
from uuid import (
    UUID,
    uuid4,
)

from wiga.connections import base
from wiga.core import Backgroundable

from .game_state import GameState
from .message import Message, Topic

logger = logging.getLogger(__name__)


class Phase(Enum):
    GATHERING = "GATHERING"
    PLAYING = "PLAYING"
    FINALIZED = "FINALIZED"


@dataclass(slots=True, kw_only=True)
class Lobby(Backgroundable):
    id: UUID = field(default_factory=uuid4)
    title: str | None = None
    password: str | None = None
    phase: Phase = Phase.GATHERING
    connections: set[base.IncomingConnection] = field(default_factory=set)
    players_limit: int | None = None
    fps: float = 30.0
    state: GameState | None = None
    task_names = ("run",)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def __hash__(self):
        return hash(self.id)

    async def run(self):
        for connection in self.connections:
            logger.debug("Sending approval")
            await connection.send(
                Message(
                    topic=Topic.MENU,
                    content={"result": "match_found"},
                    connection=connection,
                ),
            )
            logger.debug("Sent approval")
        fps = self.fps
        while self.phase != Phase.FINALIZED:
            self.state.update()
            await self.send_messages()
            till_next_frame = (
                1.0 - (datetime.utcnow().timestamp() * fps) % 1.0
            ) / fps
            await asyncio.sleep(till_next_frame)
        await self.send_messages()

    async def send_messages(self):
        async with self.lock:
            for connection in self.connections:
                perspective = self.state.get_perspective(
                    seen_by=connection.player,
                )
                await connection.send_perspective(perspective)
