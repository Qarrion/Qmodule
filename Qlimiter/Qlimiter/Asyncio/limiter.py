import logging
import asyncio
import signal

from typing import  Literal, List, Coroutine

from Qlimiter.Asyncio import Msg
from Qlimiter.Asyncio import Job


class Limiter:
    def __init__(self, max_calls:int, seconds:float,
                 limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        
        self.job = Job(max_calls,seconds,limit,logger)

        self.msg = Msg(logger, "async")
        self.msg.info.strm_initiate(max_calls, seconds)

        self._max_calls = max_calls
        self._stop_event = asyncio.Event()
        
    # -------------------------------- worker -------------------------------- #
    # def worker_coros(self, max_worker:int)->List[Coroutine]:
    #     """>>> tasks = asyncio.gather(*worker_coros(max_woker))
    #     >>> await tasks"""
    #     return [self.worker_coro() for _ in range(max_worker)]
    
    
    async def worker_taskgroup(self, interrupt=True):

        if interrupt:
            signal.signal(signal.SIGINT, self.signal_handler)

        async with asyncio.TaskGroup() as tg:
            self.tasks = [tg.create_task(self.worker_coro()) for i in range(self._max_calls)]

        print("TaskGroup Quit!")

    async def worker_coro(self):
        self.msg.debug.strm_worker('start')
        # try: 
        while not self._stop_event.is_set():
            try:
                fname, args, kwargs = await asyncio.wait_for(self.job.queue.get(), timeout=1)
                assert fname in self.job.registry.keys(), 'no fname'
                result = await self.job.handler(fname,*args, **kwargs)
                self.job.queue.task_done()

            except asyncio.TimeoutError:
                continue # wait_for(time_out)

        print("a worker quit")

    def signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'level', debug=True)
    limiter = Limiter(3, 1, 'outflow', logger=logger)

    async def myfunc1(x):
        await asyncio.sleep(x)

    async def myfunc2(x):
        raise Exception("raise Error")

    async def main():
        limiter.job.register_sync(myfunc1)
        limiter.job.register_sync(myfunc2)
        # -------------------------------------------------------------------- #
        # await limiter.job.handlers('myfunc1', 1)
        # await limiter.job.handlers('myfunc2', 1)
        # -------------------------------------------------------------------- #
        # await asyncio.gather(limiter.consume_coro(), limiter.dispatch_coro('myfunc1', 1))
        # -------------------------------------------------------------------- #

        await limiter.job.enqueue_coro('myfunc1',0.1),
        await limiter.job.enqueue_coro('myfunc1',0.1),
        await limiter.job.enqueue_coro('myfunc2',0.1),
        await limiter.job.enqueue_coro('myfunc1',0.1),
        await limiter.job.enqueue_coro('myfunc1',0.1),
        await limiter.job.enqueue_coro('myfunc1',0.1),
        await limiter.job.enqueue_coro('myfunc1',0.1),

        await limiter.worker_taskgroup()


        # coros = limiter.worker_coros(2)

        # try:
        #     async with asyncio.TaskGroup() as tg:
        #         tasks = [tg.create_task(coro) for coro in coros]
        #         puts = [tg.create_task(disp) for disp in dispatches]

        # except asyncio.CancelledError:
        #     limiter._stop_event.is_set()
        #     print("cancel")

        # finally:
        #     for t in tasks:
        #         print(t)
        #     for p in puts:
        #         print(p)
        # except KeyboardInterrupt:
        #     print("interrupt")

     
        # except asyncio.CancelledError:
        #     print("?>")

        # limiter._stop_event.set()

    # def signal_handler(sig, frame):
    #     logger.info("KeyboardInterrupt가 감지되었습니다, stop_event를 설정합니다.")


    #     all_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    #     for task in all_tasks:
    #         task.cancel()

        
    # signal.signal(signal.SIGINT, signal_handler)
    # try :
    asyncio.run(main())
    # except KeyboardInterrupt:
