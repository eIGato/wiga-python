__all__ = ["Listener"]

import asyncio
import typing as ty
from abc import ABC

from wiga import Codec
from wiga.core.background import Backgroundable
from wiga.server.connections import Connection


class Listener(Backgroundable, ABC):
    connection_class: ty.Type[Connection]
    messages: asyncio.Queue | None = None

    def __init__(self, codec: Codec):
        super().__init__()
        self.codec = codec
