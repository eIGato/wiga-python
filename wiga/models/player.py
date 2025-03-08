__all__ = ["Player"]

from dataclasses import dataclass

from .lobby import Lobby


@dataclass(slots=True, kw_only=True)
class Player:
    name: str = "Anonymous"
    lobby: Lobby | None = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.name!r})"
