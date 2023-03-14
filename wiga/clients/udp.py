import asyncio
import typing as ty

from wiga import (
    Codec,
    Message,
)
from wiga.core import (
    ADDR,
    UdpProtocol,
)
from wiga.server.connections import UdpConnection

from .base import Client


class UdpClient(Client):
    sock: asyncio.DatagramTransport | None = None

    def __init__(
        self,
        codec: Codec,
        host: str,
        port: int = 113,
        keepalive_interval: float = 5.0,
    ):
        super().__init__(codec=codec)
        self.connection_by_addr: dict[ADDR, UdpConnection] = {}
        self.host = host
        self.port = port
        self.keepalive_interval = keepalive_interval

    async def send(self, message: Message):
        data = self.codec.encode(message)
        self.sock.sendto(data, (self.host, self.port))

    async def run(self):
        datagrams = asyncio.Queue()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(datagrams=datagrams),
            remote_addr=(self.host, self.port),
        )
        self.sock = ty.cast(asyncio.DatagramTransport, transport)
        try:
            while True:
                data, addr = await datagrams.get()
                message = self.codec.decode(data)
                handler = self.handler_by_topic.get(message.topic, None)
                if handler is not None:
                    await handler(message)
        finally:
            self.sock = None
            transport.close()
