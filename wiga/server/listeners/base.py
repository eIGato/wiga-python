__all__ = ["Listener"]

import asyncio
import typing as ty
from abc import ABC

from wiga import Codec, models
from wiga.connections import Connection
from wiga.core.background import Backgroundable


class Listener(Backgroundable, ABC):
    connection_class: ty.Type[Connection]
    incoming_messages: asyncio.Queue[models.Message] | None = None

    def __init__(self, codec: Codec):
        super().__init__()
        self.codec = codec
