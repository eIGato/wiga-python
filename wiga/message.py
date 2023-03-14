__all__ = [
    "Message",
    "Topic",
]

import typing as ty
from dataclasses import (
    dataclass,
    field,
)
from enum import Enum


class Topic(Enum):
    NO_TOPIC = 0
    KEEPALIVE = 1


@dataclass(slots=True)
class Message:
    topic: Topic
    content: ty.Any
    metadata: dict[str, ty.Any] = field(default_factory=dict)
