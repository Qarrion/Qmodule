import logging
import threading
import time

import asyncio
from typing import Callable, Literal
from functools import wraps

from Qlimiter.Asyncio import CustomMsg
from Qlimiter.Asyncio import Task

class Limiter:
    def __init__(self, max_calls:int, seconds:float,
                 limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        self.task = Task(max_calls,seconds,limit,logger)

        self.msg=CustomMsg(logger, "async")
        self.msg.info.strm_initiate(max_calls, seconds)

        self._max_calls = max_calls
        self._stop_event = asyncio.Event()

    # async def _start_taskgroup(self):
    #     self.msg.debug.strm_workerpool('start')
    #     async with asyncio.TaskGroup() as tg:
    #         self.tasks = [tg.create_task(self.worker()) for _ in range(self._max_calls)]

    async def start_async_task_workers(self):
        self.workers = [asyncio.create_task(self.worker_coroutine()) for i in range(self._max_calls)]
        for worker in self.workers:
            await worker

    async def worker_coroutine(self):
        self.msg.debug.strm_worker('start')
        while not self._stop_event.is_set():
            try:
                fname, args, kwargs = await asyncio.wait_for(self.task.func_queue.get(), timeout=1)
                assert fname in self.task.func_dict.keys()
                await self.task.func_dict[fname](*args, **kwargs)
                self.task.func_queue.task_done()

            except asyncio.TimeoutError:
                continue

        print("a worker quit")
                
if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'level', debug=True)
    limiter = Limiter(3, 1, 'outflow', logger=logger)

    async def myfunc1(x):
        await asyncio.sleep(x)

    async def myfunc2(x):
        raise Exception("raise Error")

    async def main():
        limiter.task.register(myfunc1)
        limiter.task.register(myfunc2)

        # await limiter.task.func_dict['myfunc1'](1)
        # await limiter.task.func_dict['myfunc2'](1)
        # await limiter.start_async_task_workers()
        task = asyncio.create_task(limiter.worker_coroutine())
        await task
        await limiter.task.enqueue('myfunc1',0.1)
        # await limiter.task.enqueue('myfunc1',0.1)
        # await limiter.task.enqueue('myfunc2',0.1)
        # await limiter.task.enqueue('myfunc1',0.1)
        # await limiter.task.enqueue('myfunc1',0.1)
        # await limiter.task.enqueue('myfunc1',0.1)
        # await limiter.task.enqueue('myfunc1',0.1)

        # asyncio.gather()

    asyncio.run(main())
        
