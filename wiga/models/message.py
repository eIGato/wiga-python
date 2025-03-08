from __future__ import annotations

__all__ = [
    "Message",
    "Topic",
]

import typing as ty
from dataclasses import dataclass
from enum import Enum

from wiga import connections


class Topic(Enum):
    NO_TOPIC = "NO_TOPIC"
    KEEPALIVE = "KEEPALIVE"
    AUTH = "AUTH"
    MENU = "MENU"
    LOBBY = "LOBBY"


@dataclass(slots=True, kw_only=True)
class Message:
    topic: Topic
    content: ty.Any
    connection: connections.Connection | None = None
