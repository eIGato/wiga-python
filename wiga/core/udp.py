__all__ = [
    "ADDR",
    "UdpProtocol",
]

import asyncio

ADDR = tuple[str, int]


class UdpProtocol(asyncio.DatagramProtocol):
    __slots__ = ("datagrams",)

    def __init__(self, *args, datagrams: asyncio.Queue, **kwargs):
        super().__init__(*args, **kwargs)
        self.datagrams = datagrams

    def datagram_received(self, data: bytes, addr: ADDR):
        self.datagrams.put_nowait((data, addr))
