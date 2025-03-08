__all__ = ["Backgroundable"]

import asyncio
import logging
from abc import ABC

logger = logging.getLogger(__name__)


class Backgroundable(ABC):
    __tasks: list[asyncio.Task] | None = None
    task_names: tuple[str, ...] = ()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        return False

    async def start(self):
        type_name = type(self).__name__
        if self.__tasks is not None:
            raise RuntimeError(f"{type_name} already started")
        logger.info(f"Starting {type_name}")
        self.__tasks = tasks = []
        try:
            for name in set(self.task_names):
                method = getattr(self, name)
                task = asyncio.create_task(method())
                tasks.append(task)
            logger.info(f"Started {type_name}")
        except BaseException:
            logger.error("Start failed, stopping")
            await self.stop()
            raise

    async def stop(self):
        type_name = type(self).__name__
        tasks, self.__tasks = self.__tasks, None
        if tasks is None:
            return
        logger.info(f"Stopping {type_name}")
        for task in tasks:
            task.cancel()
        done, pending = await asyncio.wait(tasks, timeout=1)
        results = await asyncio.gather(*done, return_exceptions=True)
        for exception in filter(lambda r: isinstance(r, Exception), results):
            logger.exception("Exception in task:", exc_info=exception)
        if pending:
            logger.warning(f"{type_name} could not stop in 1 second.")
        else:
            logger.info(f"Stopped {type_name}")
