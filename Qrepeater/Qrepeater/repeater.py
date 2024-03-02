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
    """
    register func 안에 반드시 unit value 이전에 작업이 안전하게 종료 되도록 timeout 로직 필요
    timeout 은 task를 강제 종료 하지 못함, -> 루프 종료 선택
    """
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.tracer = Tracer(logger, 'thread')
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
            while not self._stop_event.wait(self.timer.remaining_seconds()):
                futures = [executor.submit(job) for job in self._jobs]

                for future in as_completed(futures,timeout=4):
                    try:
                        future.result()
                    except Exception as e:      #* submit error
                        print(e)

        except TimeoutError as e:               #* timeout error
            self.tracer.error.catch(e)

        except KeyboardInterrupt as e:
            self.tracer.error.catch(e)

        finally:
            self._stop_event.set()
            executor.shutdown(wait=True)


class AsyncRepeater:
    
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.tracer = Tracer(logger, 'async')
        self.timer = Timer(value, unit, logger)

        self._stop_event = asyncio.Event()
        self._jobs = list()

    async def _wrapper_timeout(self, func:Callable, *args):
        # timeout = self.timer.remaining_seconds()-1
        timeout = 2.5
        try:                            #! execution
            await asyncio.wait_for(func(*args), timeout=timeout)
        except asyncio.TimeoutError:    #! timeout 
            self.tracer.warning.strm_async_timeout(func.__name__, args, timeout)
            
    def register(self, func:Callable, *args, **kwargs):
        self._jobs.append(partial(self._wrapper_timeout, func, *args, **kwargs))

    async def start_with_async(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.timer.remaining_seconds())
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(job()) for job in self._jobs]

if __name__ == "__main__":
    from Qrepeater.utils.log_color import ColorLog
    # thread_logger = ColorLog('test','blue')
    async_logger = ColorLog('test','blue')
    main_logger = ColorLog('func','green')
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
    # -------------------------------- thread -------------------------------- #
    # repeater = ThreadRepeater(5, 'second', thread_logger)

    # def myfunc(x):
    #     main_logger.warning(f'myfunc{x} sleep ({x})')
    #     time.sleep(x)
    #     main_logger.warning(f'myfunc{x} done!')

    # # from functools import partial
    # repeater.register(myfunc, 1)
    # repeater.register(myfunc, 2)
    # repeater.register(myfunc, 3)
  
    # repeater.start_with_thread()
