#!/usr/bin/env python3
import asyncio

from aioconsole import ainput, aprint

from wiga import (
    JsonCodec,
    Message,
    Topic,
)
from wiga.client import Client
from wiga.connections import OutgoingUdpConnection
from wiga.connections.udp import DEFAULT_PORT


class TicTacToeClient(Client):
    connection_class = OutgoingUdpConnection
    authorized = False
    match_found = False
    last_state = None

    async def handle_auth_message(self, message: Message):
        if message.content == "success":
            self.authorized = True
            await self.send(
                Message(topic=Topic.MENU, content={"command": "find_match"})
            )
        else:
            await self.send(
                Message(topic=Topic.AUTH, content={"name": await ainput("Name: ")})
            )

    async def handle_menu_message(self, message: Message):
        if message.content.get("result", None) == "match_found":
            self.match_found = True

    async def handle_lobby_message(self, message: Message):
        # The most primitive implementation
        if message.content == self.last_state:
            return
        await aprint(message.content)
        if "id" not in message.content:
            return
        self.last_state = message.content
        if self.last_state["winner"]:
            self.match_found = False

    async def console_input(self):
        if not self.match_found:
            await asyncio.sleep(0.1)
        content = 0
        while True:
            try:
                content = int(await ainput("Coordinates: "))
            except ValueError:
                continue
            break
        await self.send(
            Message(topic=Topic.LOBBY, content=content)
        )


async def main():
    host = await ainput("Host[127.0.0.1]: ") or "127.0.0.1"
    client = TicTacToeClient(codec=JsonCodec(), addr=(host, DEFAULT_PORT))
    client.add_handler(topic=Topic.AUTH, handler=client.handle_auth_message)
    client.add_handler(topic=Topic.MENU, handler=client.handle_menu_message)
    client.add_handler(topic=Topic.LOBBY, handler=client.handle_lobby_message)
    async with client:
        await client.send(
            Message(topic=Topic.AUTH, content={"name": await ainput("Name: ")})
        )
        while True:
            await ainput("Press Enter to find a match.")
            await client.send(
                Message(topic=Topic.MENU, content={"command": "find_match"})
            )
            while not client.match_found:
                await asyncio.sleep(0.1)
            await aprint("Match found")
            while client.match_found and (not client.last_state or not client.last_state["winner"]):
                await client.console_input()


if __name__ == "__main__":
    asyncio.run(main())
