__all__ = ["Backgroundable"]

import asyncio
import logging
from abc import (
    ABC,
    abstractmethod,
)

logger = logging.getLogger(__name__)


class Backgroundable(ABC):
    __task: asyncio.Task | None = None

    async def start(self) -> asyncio.Task:
        if self.__task is None:
            self.__task = asyncio.create_task(self.run())
        return self.__task

    async def stop(self):
        task, self.__task = self.__task, None
        if task is None:
            return
        task.cancel()
        _, pending = await asyncio.wait({task}, timeout=1)
        if pending:
            logger.warning(f"{self} could not stop in 1 second.")

    @abstractmethod
    async def run(self):
        pass
