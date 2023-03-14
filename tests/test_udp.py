import asyncio

from wiga import (
    JsonCodec,
    Message,
    Topic,
)
from wiga.clients import UdpClient
from wiga.server import (
    App,
    UdpListener,
)


def build_handler(prefix):
    async def handle(message):
        connection = message.metadata.get("connection", None)
        print(prefix, message.content, connection and connection.port)
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
    server.add_listener(UdpListener(port=9999, codec=JsonCodec()))
    server.add_handler(Topic.NO_TOPIC, build_handler("[Server]"))
    client1 = UdpClient(codec=JsonCodec(), host="127.0.0.1", port=9999)
    client1.add_handler(Topic.NO_TOPIC, build_handler("[Client1]"))
    client2 = UdpClient(codec=JsonCodec(), host="127.0.0.1", port=9999)
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
    print(connection_by_addr)
    for connection in connection_by_addr.values():
        await connection.send(
            Message(topic=Topic.NO_TOPIC, content="sent by server")
        )
    for connection in connection_by_addr.values():
        await connection.send(
            Message(topic=Topic.NO_TOPIC, content="sent by server")
        )
    await asyncio.sleep(1)
