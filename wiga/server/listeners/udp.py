import asyncio
import logging
import typing as ty

from wiga import Codec
from wiga.connections.udp import (
    ADDR,
    DEFAULT_PORT,
    IncomingUdpConnection,
    UdpProtocol,
)

from .base import Listener

logger = logging.getLogger(__name__)


class UdpListener(Listener):
    connection_class: ty.Type[IncomingUdpConnection] = IncomingUdpConnection
    task_names = ("run",)

    def __init__(self, codec: Codec, addr: ADDR = ("0.0.0.0", DEFAULT_PORT)):
        super().__init__(codec=codec)
        self.connection_by_addr: dict[ADDR, IncomingUdpConnection] = {}
        self.addr = addr

    async def run(self):
        datagrams = asyncio.Queue()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UdpProtocol(datagrams=datagrams),
            local_addr=self.addr,
        )
        transport = ty.cast(asyncio.DatagramTransport, transport)
        try:
            while True:
                data, addr = await datagrams.get()
                logger.info(f"Got {data=} from {addr=}")
                connection = self.connection_by_addr.get(addr, None)
                if connection is None:
                    logger.info(f"Got new connection from {addr=}")
                    connection = self.connection_class(
                        incoming_messages=self.incoming_messages,
                        codec=self.codec,
                        addr=addr,
                        transport=transport,
                    )
                    self.connection_by_addr[addr] = connection
                    await connection.start()
                await connection.on_receive(data)
        except Exception as e:
            logger.exception("Exception occurred:", exc_info=e)
            raise
        finally:
            transport.close()
