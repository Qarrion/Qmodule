import logging
from typing import Literal, Coroutine

from functools import partial

import asyncio
from Qrepeater.timer import Timer
from Qrepeater.msg import Msg


class Repeater:
    
    def __init__(self, value:float, unit:Literal['second','minute','hour'], logger:logging.Logger):
        self.msg = Msg(logger, 'async')
        self.timer = Timer(value, unit, self.msg)

        self._stop_event = asyncio.Event()
        self._jobs = list()

    def register(self, func:Coroutine, args:tuple=(), kwargs:dict=None, timeout:float=None):
        self._jobs.append(partial(self._wrapper_job, func, args, kwargs, timeout))

    async def run(self):
        await asyncio.sleep(self.timer.remaining_seconds())
        while not self._stop_event.is_set():
            async with asyncio.TaskGroup() as tg:
                for i, job in enumerate(self._jobs):
                    tg.create_task(job(),name = f'repeater-{i}')
            await asyncio.sleep(self.timer.remaining_seconds())
            
    async def _wrapper_job(self,func:Coroutine, args:tuple=(), kwargs:dict=None, timeout:float=None):
        self.msg.job('start',func.__name__)
        if kwargs is None: kwargs={}
        if timeout is not None:
            try:                            #! execution
                await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:    #! timeout 
                self.msg.warning.exception(func.__name__, args, timeout)
        else:
            await func(*args, **kwargs)
        self.msg.info.job('finish',func.__name__)

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('main','head')

    # -------------------------------- asyncio ------------------------------- #
    async def myfunc(x):
        await asyncio.sleep(x)

    async def main():
        repeater = Repeater(value=10, unit='second', logger=logger)

        repeater.register(myfunc,(6,),timeout=8)
        repeater.register(myfunc,(9,),timeout=8)
        repeater.register(myfunc,(12,),timeout=8)

        await repeater.run()

    asyncio.run(main())
