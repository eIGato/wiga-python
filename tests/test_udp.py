import asyncio

from wiga import (
    JsonCodec,
    Message,
    Topic,
)
from wiga.client import Client
from wiga.connections import OutgoingUdpConnection
from wiga.server import (
    App,
    UdpListener,
)


class UdpClient(Client):
    connection_class = OutgoingUdpConnection


def build_handler(prefix):
    async def handle(message):
        connection = message.connection
        print(prefix, message.content, connection and connection.addr)
        if connection:
            await connection.send(
                Message(
                    topic=Topic.NO_TOPIC,
                    content=f"accepted: {message.content}",
                )
            )

    return handle


async def test_udp_clients_are_served_independently():
    server = App()
    server.add_listener(UdpListener(codec=JsonCodec()))
    server.add_handler(Topic.NO_TOPIC, build_handler("[Server]"))
    client1 = UdpClient(codec=JsonCodec())
    client1.add_handler(Topic.NO_TOPIC, build_handler("[Client1]"))
    client2 = UdpClient(codec=JsonCodec())
    client2.add_handler(Topic.NO_TOPIC, build_handler("[Client2]"))
    await server.start()
    await client1.start()
    await client2.start()
    await asyncio.sleep(1)

    await client1.send(
        Message(topic=Topic.NO_TOPIC, content="sent by client1")
    )
    await client2.send(
        Message(topic=Topic.NO_TOPIC, content="sent by client2")
    )
    await client1.send(
        Message(topic=Topic.NO_TOPIC, content="sent by client1")
    )
    await client2.send(
        Message(topic=Topic.NO_TOPIC, content="sent by client2")
    )
    await asyncio.sleep(1)

    connection_by_addr = next(iter(server.listeners)).connection_by_addr
    # print(connection_by_addr)
    for addr, connection in connection_by_addr.items():
        await connection.send(
            Message(topic=Topic.NO_TOPIC, content=f"sent to {addr=}")
        )
    for addr, connection in connection_by_addr.items():
        await connection.send(
            Message(topic=Topic.NO_TOPIC, content=f"sent to {addr=}")
        )
    await asyncio.sleep(1)
    await client1.stop()
    await client2.stop()
    await server.stop()


if __name__ == "__main__":
    asyncio.run(test_udp_clients_are_served_independently())
