from __future__ import annotations

__all__ = [
    "IncomingUdpConnection",
    "OutgoingUdpConnection",
    "UdpConnection",
]

import asyncio
import typing as ty
from dataclasses import dataclass

from wiga import models

from .base import Connection, OutgoingConnection, IncomingConnection

ADDR = tuple[str, int]
DATAGRAM = tuple[bytes, ADDR]
DEFAULT_PORT = 8233
assert DEFAULT_PORT == 8000 + sum(b'UDP')


class UdpProtocol(asyncio.DatagramProtocol):
    datagrams: asyncio.Queue[DATAGRAM]
    __slots__ = ("datagrams",)

    def __init__(self, *args, datagrams: asyncio.Queue[DATAGRAM], **kwargs):
        super().__init__(*args, **kwargs)
        self.datagrams = datagrams

    def datagram_received(self, data: bytes, addr: ADDR):
        self.datagrams.put_nowait((data, addr))


@dataclass(slots=True, kw_only=True)
class UdpConnection(Connection):
    task_names = Connection.task_names + ("keepalive",)
    addr: ADDR = ("127.0.0.1", DEFAULT_PORT)
    transport: asyncio.DatagramTransport | None = None
    keepalive_interval: float = 5.0

    def __hash__(self):
        return hash(self.addr)

    async def send(self, message: models.Message):
        data = self.codec.encode(message)
        self.transport.sendto(data, self.addr)

    async def keepalive(self):
        while True:
            if self.transport is not None:
                await self.send(
                    models.Message(topic=models.Topic.KEEPALIVE, content=None)
                )
            await asyncio.sleep(self.keepalive_interval)


@dataclass(slots=True, kw_only=True)
class IncomingUdpConnection(IncomingConnection, UdpConnection):
    task_names = IncomingConnection.task_names + UdpConnection.task_names

    def __hash__(self):
        return hash(self.addr)


@dataclass(slots=True, kw_only=True)
class OutgoingUdpConnection(OutgoingConnection, UdpConnection):
    task_names = OutgoingConnection.task_names + UdpConnection.task_names

    def __hash__(self):
        return hash(self.addr)

    async def connect(self):
        datagrams = asyncio.Queue()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(datagrams=datagrams),
            remote_addr=self.addr,
        )
        self.transport = ty.cast(asyncio.DatagramTransport, transport)
        try:
            while True:
                data, addr = await datagrams.get()
                message = self.codec.decode(data)
                await self.incoming_messages.put(message)
        finally:
            self.transport = None
            transport.close()
