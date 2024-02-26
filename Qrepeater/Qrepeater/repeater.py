import time
import logging
import threading
from typing import Literal, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import asyncio

from Qrepeater.tracer import Tracer
from Qrepeater.timer import Timer


class ThreadRepeater:

    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.msg = Tracer(logger, 'thread')
        self.timer = Timer(value, unit, logger)

        self._stop_event = threading.Event()
        self._jobs = list()
    
    def register(self, func:Callable, *args):
        if args:
            self._jobs.append(partial(func,*args))
        else:
            self._jobs.append(func)

    def start_with_thread(self):
        executor = ThreadPoolExecutor(len(self._jobs), 'worker')
        
        try:
            while not self._stop_event.wait(self.timer.remaining_seconds(debug=True)):
                futures = [executor.submit(job) for job in self._jobs]
            self.msg.info.strm_thread_alldone()
                
        except KeyboardInterrupt:
            print('Keyboard Interrupted!')

        finally:
            self._stop_event.set()
            executor.shutdown(wait=True)
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)

class AscyncRepeater:
    
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.msg = Tracer(logger, 'async')
        self.timer = Timer(value, unit, logger)

        self._stop_event = asyncio.Event()
        self._jobs = list()

    async def _wrapper_timeout(self, func:Callable, *args):
        timeout = self.timer.remaining_seconds()-1
        try:                            #! execution
            await asyncio.wait_for(func(*args), timeout=timeout)
        except asyncio.TimeoutError:    #! timeout 
            self.msg.warning.strm_async_timeout(func.__name__, args, timeout)
            
    def register(self, func:Callable, *args):
        if args:
            self._jobs.append(partial(self._wrapper_timeout, func, *args))
        else:
            self._jobs.append(partial(self._wrapper_timeout, func))
 
    async def start_with_async(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.timer.remaining_seconds(debug=True))
            async with asyncio.TaskGroup() as tg:
                for job in self._jobs:
                    tg.create_task(job())
            print('all tasks done!')
                



if __name__ == "__main__":
    from Qrepeater.utils.log_color import ColorLog
    logger1 = ColorLog('test','blue')
    logger2 = ColorLog('func','green')

    # -------------------------------- thread -------------------------------- #
    repeater = ThreadRepeater(10, 'second', logger1)

    def myfunc1(x):
        logger2.warning(f'myfunc1 sleep ({x})')
        time.sleep(x)
        logger2.warning(f'myfunc1 done!')

    def myfunc2(x):
        logger2.warning(f'myfunc2 sleep ({x})')
        time.sleep(x)
        logger2.warning(f'myfunc2 done!')

    # from functools import partial
    repeater.register(myfunc1, 1)
    repeater.register(myfunc2, 2)

    repeater.start_with_thread()
    # -------------------------------- asyncio ------------------------------- #
    # async def main():
    #     repeater = AscyncRepeater(5, 'second', logger)

    #     async def myfunc1(x):
    #         logger2.warning(f'myfunc1 sleep ({x})')
    #         await asyncio.sleep(x)
    #         logger2.warning(f'myfunc1 done!')


    #     async def myfunc2(x):
    #         logger2.warning(f'myfunc2 sleep ({x})')
    #         await asyncio.sleep(x)
    #         logger2.warning(f'myfunc2 done!')

    #     repeater.register(myfunc1, 4.2)
    #     repeater.register(myfunc2, 4.1)

    #     await repeater.start_with_async()
    
    # asyncio.run(main())