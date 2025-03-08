#!/usr/bin/env python3
import asyncio
import logging
import os
import random
from dataclasses import dataclass

from wiga import (
    GameState,
    JsonCodec,
    Lobby,
    Message,
    Phase,
    Player,
    Topic,
)
from wiga.server import (
    App,
    UdpListener,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class TicTacToeState(GameState):
    grid: str = " " * 9
    player_x: Player
    player_o: Player
    winner: str | None = None

    def __json__(self):
        return {
            "id": self.id,
            "grid": self.grid,
            "player_x": self.player_x.name,
            "player_o": self.player_o.name,
            "winner": self.winner,
        }

    def update(self):
        pass

    def get_perspective(self, seen_by: Player):
        return self


@dataclass(slots=True, kw_only=True)
class TicTacToeLobby(Lobby):
    state: TicTacToeState

    def __init__(self, **kwargs):
        logger.info("Initializing TicTacToeLobby")
        connections = list(kwargs["connections"])
        random.shuffle(connections)
        for connection in connections:
            connection.player.lobby = self
        super(TicTacToeLobby, self).__init__(
            **kwargs,
            state=TicTacToeState(
                id=1,
                player_x=connections[0].player,
                player_o=connections[1].player,
            ),
        )
        logger.info("Initialized TicTacToeLobby")

    def __hash__(self):
        return hash(self.id)

    async def handle_message(self, message: Message):
        async with self.lock:
            return await self._handle_message(message)

    async def _handle_message(self, message: Message):
        player = message.connection.player
        state = self.state
        if (
            player is state.player_x
            and not state.id & 1
            or player is state.player_o
            and state.id & 1
        ):
            await message.connection.send(
                Message(
                    topic=Topic.LOBBY,
                    content={"error": "Not your turn"},
                ),
            )
            return
        if not isinstance(message.content, int):
            await message.connection.send(
                Message(
                    topic=Topic.LOBBY,
                    content={"error": "Invalid message"},
                ),
            )
            return
        y, x = divmod(message.content, 10)
        if not all([1 <= digit <= 3 for digit in (x, y)]):
            await message.connection.send(
                Message(
                    topic=Topic.LOBBY,
                    content={"error": "Incorrect coordinates"},
                ),
            )
            return
        x -= 1
        y -= 1
        idx = x + 3 * y
        if self.state.grid[idx] != " ":
            await message.connection.send(
                Message(
                    topic=Topic.LOBBY,
                    content={"error": "Cell is busy"},
                ),
            )
            return
        char = "X" if state.id & 1 else "O"
        grid = self.state.grid = self.state.grid[:idx] + char + self.state.grid[idx + 1 :]
        if char * 3 in {
            grid[:3],
            grid[3:6],
            grid[6:],
            grid[0:7:3],
            grid[1:8:3],
            grid[2:9:3],
            grid[0:9:4],
            grid[2:7:2],
        }:
            self.state.winner = char
            self.phase = Phase.FINALIZED
            return
        self.state.id += 1



class TicTacToeApp(App):
    player_connections: set
    task_names = App.task_names + ("matchmaking",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_connections = set()
        self.lobbies = set()

    async def handle_menu_message(self, message: Message):
        connection = message.connection
        logger.info("Got menu message")
        command = message.content.get("command")
        logger.debug(f"Conditions: {command=}, {connection.player=}")
        if (
            command == "find_match"
            and connection.player is not None
            and connection.player.lobby is None
        ):
            logger.info("Adding connection to pool")
            self.player_connections.add(connection)

    async def matchmaking(self):
        while True:
            logger.info("Making matches")
            while len(self.player_connections) < 2:
                await asyncio.sleep(0.1)
            logger.info("Got enough players")
            player_connections = {self.player_connections.pop() for _ in range(2)}
            logger.info("Creating lobby")
            lobby = TicTacToeLobby(connections=player_connections)
            self.lobbies.add(lobby)
            logger.info("Starting lobby")
            await lobby.start()


async def handle_auth_message(message: Message):
    message.connection.player = Player(name=message.content["name"])


async def handle_lobby_message(message: Message):
    lobby = message.connection.player.lobby
    if lobby.phase is Phase.FINALIZED:
        return
    await lobby.handle_message(message)


async def main():
    app = TicTacToeApp()
    app.add_handler(topic=Topic.AUTH, handler=handle_auth_message)
    app.add_handler(topic=Topic.MENU, handler=app.handle_menu_message)
    app.add_handler(topic=Topic.LOBBY, handler=handle_lobby_message)
    app.add_listener(UdpListener(codec=JsonCodec()))
    async with app:
        await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "DEBUG")))
    logger.info("Running")
    asyncio.run(main())
