import logging
import asyncio
import signal

from typing import  Literal, List, Coroutine

from Qlimiter.msg import Msg
from Qlimiter.job import Job

class Limiter:
    """>>> #
    limiter = Limiter(3, 1, 'outflow', logger=logger)
    limiter.register(func:Coroutine, fname:str=None)
    await limiter.enqueue(self, fname:str, args=(), kwargs={}, retry=0)
    await limiter.taskgroup()
    retry - semaphore
    """
    def __init__(self, max_calls:int, seconds:float, limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        
        self.msg = Msg(logger, 'async')
        self.msg.info.initiate(max_calls, seconds)

        self.job = Job(max_calls,seconds,limit, self.msg)
        self._stop_event = asyncio.Event()
    
    async def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        async with asyncio.TaskGroup() as tg:
            for i in range(self.job._max_worker):
                task = tg.create_task(self._worker_coro(),name=f'limiter-{i}')
        print("TaskGroup Quit!")

    def register(self, func:Coroutine, fname:str=None):
        self.job.register(func, fname)

    async def enqueue(self, fname:str, args:tuple=(), kwargs:dict=None, retry:int=0):
        await self.job.enqueue(fname, args,kwargs, retry)

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

    async def myfunc1(a,b,c):

        await asyncio.sleep(1)

    async def myfunc2(x):
        raise Exception("raise Error")

    async def main():
        limiter.register(myfunc1)
        limiter.register(myfunc2)

        await limiter.enqueue('myfunc1',(1,2,3))
        await limiter.enqueue('myfunc1',(1,2,3))

        # await limiter.enqueue('myfunc1',(1,2,3))
        await limiter.enqueue('myfunc2',(2,))
        # await limiter.enqueue('myfunc2',(3,))
        # await limiter.enqueue('myfunc1',(1,))
        # await limiter.enqueue('myfunc1',(2,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(3,))
        # await limiter.enqueue('myfunc1',(1,))

        await limiter.run()
    asyncio.run(main())

