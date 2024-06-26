# -------------------------------- ver 240511 -------------------------------- #
# tools

import logging
from Qutils.logger_custom import CustomLog
from Qutils.format_time import TimeFormat
from typing import Callable, Literal

import asyncio, time


class Limit:
    """
    >>> # initiate
    limiter = Limiter(logger)
    limiter.set_rate(max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'])
    >>> # define
    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')

    >>> # wrapper
    xfunc_limit = limiter.wrapper(async_def:Callable, propagate=True, msg=False)

    >>> # main
    async def main():
        tasks = []
        for _ in range(10):
            task = asyncio.create_task(xfunc_limit(_))
            tasks.append(task)
        await asyncio.gather(*tasks)
    asyncio.run(main())
    """

    # def __init__(self, name:str='limiter'):
    def __init__(self, logger:logging.Logger):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg("Limiter")
        self._frame = '<limit>'

    def set_rate(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow']):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg('set_rate', limit,f"max({max_worker})",f"sec({seconds})", frame=self._frame)

    def wrapper(self, async_def:Callable, propagate=True, msg=False):
        """throttle"""
        self._custom.info.msg('wrapper', async_def.__name__,frame=self._frame)
        async def _wrapper(*args):
            propagate_exception = None

            async with self._semaphore:

                #! if msg : self._msg_semaphore('acquire',async_def.__name__)
                # ------------------------------------------------------------ #
                try: 
                    tsp_start = time.time()     
                    result = await async_def(*args)

                except Exception as e:
                    self._custom.error.msg('except',async_def.__name__,str(args),frame=self._frame)
                    propagate_exception = e
                # ------------------------------------------------------------ #
                finally:
                    tsp_finish = time.time()
                    await self._wait_reset(tsp_start, tsp_finish,msg=True)
                    #! if msg : self._msg_semaphore('release',async_def.__name__)
                    if propagate_exception and propagate: #? propagate exception to retry
                        raise propagate_exception
        return _wrapper
    
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f"({self._semaphore._value}/{self._max_worker})"
            self._custom.info.msg('acquire',fname,self._custom.arg(f'sema{queue}',2,'l',"-"),frame=self._frame)
        elif context =="release":
            queue = f"({self._semaphore._value+1}/{self._max_worker})<"
            self._custom.info.msg('release',fname,self._custom.arg(f'sema{queue}',2,'r',"-"),frame=self._frame)

    async def _wait_reset(self, tsp_start:float, tsp_finish, msg=False):

        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)
        
        if msg : self._msg_wait_reset(seconds,tsp_ref)
        if seconds > 0.0:
            await asyncio.sleep(seconds)

    def _msg_wait_reset(self, seconds:float, tsp_ref:float):
        msg_sec = TimeFormat.seconds(seconds,'hmsf')
        msg_ref = TimeFormat.timestamp(tsp_ref,'hmsf')
        self._custom.info.msg('reset',self._limit_type,msg_ref,msg_sec,frame=self._frame)


class Limiter(Limit):

    _instances = {}

    def __new__(cls, name:str='limiter', *args, **kwargs):
        if name not in cls._instances:
            instance = super(Limiter, cls).__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]
    

    def __init__(self, name:str='limiter'):
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None

        self._custom = CustomLog(logger,'async')
        self._custom.info.msg("Limiter",name)
        self._frame = '<limit>'



if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('limiter', 'head')
    limiter = Limit(logger)
    limiter.set_rate(3, 1, 'outflow')

    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')

    async def xerro(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        raise ValueError("raise error")
        # print(f'finish {x}')

    xrfunc = limiter.wrapper(xfunc,propagate=False,msg=True)
    xrerro = limiter.wrapper(xerro,propagate=False,msg=True)

    async def main():
        tasks = []
        for _ in range(5):
            try:
                if _ == 3:
                    task = asyncio.create_task(xrerro(_),name=limiter._custom.ith() )
                else:
                    task = asyncio.create_task(xrfunc(_),name=limiter._custom.ith() )
            except Exception as e:
                print(e)

        await asyncio.sleep(10)
    asyncio.run(main())


