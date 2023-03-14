import asyncio

from wiga import (
    Codec,
    Message,
    Topic,
)

from .base import Connection


class UdpConnection(Connection):
    def __init__(
        self,
        messages: asyncio.Queue,
        codec: Codec,
        host: str,
        port: int,
        sock: asyncio.DatagramTransport,
        keepalive_interval: float = 5.0,
    ):
        super().__init__(messages=messages, codec=codec)
        self.host = host
        self.port = port
        self.sock = sock
        self.keepalive_interval = keepalive_interval

    async def send(self, message: Message):
        data = self.codec.encode(message)
        self.sock.sendto(data, (self.host, self.port))

    async def run(self):
        while True:
            await self.send(Message(topic=Topic.KEEPALIVE, content=None))
            await asyncio.sleep(self.keepalive_interval)
