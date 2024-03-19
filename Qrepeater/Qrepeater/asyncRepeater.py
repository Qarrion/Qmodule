import logging
from typing import Literal, Callable

from functools import partial

import asyncio
from Qrepeater.timer import Timer
from Qrepeater.msg import Msg




class AsyncRepeater:
    
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.msg = Msg(logger, 'async')
        self.timer = Timer(value, unit, self.msg)

        self._stop_event = asyncio.Event()
        self._jobs = list()

    async def _wrapper_timeout(self, func:Callable, *args):
        timeout = 2.5
        try:                            #! execution
            await asyncio.wait_for(func(*args), timeout=timeout)
        except asyncio.TimeoutError:    #! timeout 
            self.msg.warning.strm_async_timeout(func.__name__, args, timeout)
            
    def register(self, func:Callable, *args, **kwargs):
        self._jobs.append(partial(self._wrapper_timeout, func, *args, **kwargs))

    async def start_with_async(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.timer.remaining_seconds())
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(job()) for job in self._jobs]

if __name__ == "__main__":
    from Qlogger import Logger
    main_logger = Logger('main','green')
    async_logger = Logger('main','head')
    # from Qrepeater.utils.log_color import ColorLog
    # # thread_logger = ColorLog('test','blue')
    # async_logger = ColorLog('test','blue')
    # main_logger = ColorLog('func','green')
    # -------------------------------- asyncio ------------------------------- #
    async def main():
        repeater = AsyncRepeater(5, 'second', main_logger)

        async def myfunc(x):
            async_logger.warning(f'myfunc{x} sleep ({x})')
            await asyncio.sleep(x)
            async_logger.warning(f'myfunc{x} done!')

        repeater.register(myfunc,1)
        repeater.register(myfunc,2)
        repeater.register(myfunc,3)

        await repeater.start_with_async()

    asyncio.run(main())
