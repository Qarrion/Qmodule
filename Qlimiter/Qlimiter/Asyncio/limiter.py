import logging
import asyncio
import signal

from typing import  Literal, List, Coroutine

from Qlimiter.asyncio import Msg
from Qlimiter.asyncio import Job

class Limiter:
    """>>> #
    limiter.register(func:Coroutine, fname:str=None)
    await limiter.enqueue(self, fname:str, *args, **kwargs)
    await limiter.taskgroup()
    """
    def __init__(self, max_calls:int, seconds:float, limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        
        self.msg = Msg(logger, 'async')
        self.job = Job(max_calls,seconds,limit, self.msg)

        self.msg.info.initiate(max_calls, seconds)

        self._stop_event = asyncio.Event()
    
    def register(self, func:Coroutine, fname:str=None):
        self.job.register(func, fname)

    async def enqueue(self, fname:str, *args, **kwargs):
        await self.job.enqueue(fname, *args, **kwargs)

    async def taskgroup(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        self.background_tasks = set()
        async with asyncio.TaskGroup() as tg:
            for _ in range(self.job._max_worker):
                task = tg.create_task(self._worker_coro())
                self.background_tasks.add(task)

        print("TaskGroup Quit!")

    async def _worker_coro(self):
        while not self._stop_event.is_set():
            result = await self.job.dequeue()
        print('a worker quit')

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'head', debug=True)
    logger._dev_stream_handler_level('INFO')
    limiter = Limiter(3, 1, 'outflow', logger=logger)

    async def myfunc1(x):
        await asyncio.sleep(x)

    async def myfunc2(x):
        raise Exception("raise Error")

    async def main():
        limiter.register(myfunc1)
        limiter.register(myfunc2)

        await limiter.enqueue('myfunc1',(1,))
        await limiter.enqueue('myfunc2',(2,))
        # await limiter.enqueue('myfunc2',(3,))
        # await limiter.enqueue('myfunc1',(1,))
        # await limiter.enqueue('myfunc1',(2,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(1,))

        await limiter.taskgroup()

    asyncio.run(main())

