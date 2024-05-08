
from Qlimiter.utils.logger_custom import CustomLog
from Qlimiter.utils.format_time import TimeFormat
from typing import Callable, Literal

import asyncio, time



class Limiter:
    """
    >>> # initiate
    limiter = Limiter()
    limiter.set_rate(3, 1, 'outflow')

    >>> # define
    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')

    >>> # wrapper
    xrfunc = limiter.wrapper(xfunc)

    >>> # main
    async def main():
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(xrfunc(_))
            tasks.append(task)
        await asyncio.gather(*tasks)
    asyncio.run(main())
    """

    def __init__(self, name:str='limiter'):
        
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None

        self._custom = CustomLog(logger,'async')
        self._custom.info.msg("Limiter")

    def set_rate(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow']):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})")

    def wrapper(self, async_def:Callable):
        """throttle"""
        async def _wrapper(*args):
            propagate_exception = None

            async with self._semaphore:
                self._msg_semaphore('acquire',async_def.__name__)
                # ------------------------------------------------------------ #
                try: 
                    tsp_start = time.time()     
                    result = await async_def(*args)

                except Exception as e:
                    self._custom.error.msg('job',async_def.__name__,str(args))
                    propagate_exception = e
                # ------------------------------------------------------------ #
                finally:
                    tsp_finish = time.time()
                    await self._wait_reset(tsp_start, tsp_finish)
                    self._msg_semaphore('release',async_def.__name__)
                    #? propagate exception to retry
                    if propagate_exception:
                        raise propagate_exception
        return _wrapper
    
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f">s({self._semaphore._value}/{self._max_worker})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({self._semaphore._value+1}/{self._max_worker})<"
            var01 = f">{queue:>11}"
        self._custom.debug.msg(context,fname,var01,frame='sema',task=True)

    async def _wait_reset(self, tsp_start:float, tsp_finish):
        #! TODO msg replace with methods _msg_xxx
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        print(tsp_ref,  self._seconds, time.time())
        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)
        msg_sec = TimeFormat.seconds(seconds,'hmsf')
        msg_ref = TimeFormat.timestamp(tsp_ref,'hmsf')

        self._custom.debug.msg(self._limit_type,f"unit s ({self._seconds})",msg_ref,msg_sec,task=True)
        
        if seconds > 0.0:
            await asyncio.sleep(seconds)


if __name__ =="__main__":
    limiter = Limiter()
    limiter.set_rate(3, 1, 'outflow')

    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')

    xrfunc = limiter.wrapper(xfunc)

    async def main():
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(xrfunc(_))
            tasks.append(task)

        await asyncio.gather(*tasks)

    asyncio.run(main())