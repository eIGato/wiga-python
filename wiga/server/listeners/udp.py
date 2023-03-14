import asyncio
import typing as ty

from wiga import Codec
from wiga.core import (
    ADDR,
    UdpProtocol,
)
from wiga.server.connections import UdpConnection

from .base import Listener


class UdpListener(Listener):
    connection_class: ty.Type[UdpConnection] = UdpConnection

    def __init__(self, codec: Codec, host: str = "0.0.0.0", port: int = 113):
        super().__init__(codec=codec)
        self.connection_by_addr: dict[ADDR, UdpConnection] = {}
        self.host = host
        self.port = port

    async def run(self):
        datagrams = asyncio.Queue()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(datagrams=datagrams),
            local_addr=(self.host, self.port),
        )
        try:
            while True:
                data, addr = await datagrams.get()
                connection = self.connection_by_addr.get(addr, None)
                if connection is None:
                    host, port = addr
                    connection = self.connection_class(
                        messages=self.messages,
                        codec=self.codec,
                        host=host,
                        port=port,
                        sock=ty.cast(asyncio.DatagramTransport, transport),
                    )
                    self.connection_by_addr[addr] = connection
                    await connection.start()
                await connection.on_receive(data)
        finally:
            transport.close()
