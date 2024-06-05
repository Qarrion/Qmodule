# -------------------------------- ver 240511 -------------------------------- #
# tools
# -------------------------------- ver 240527 -------------------------------- #
# limiter return
# -------------------------------- ver 240528 -------------------------------- #
# no wraps

import inspect
import logging
from Qtask.utils.logger_custom import CustomLog
from Qtask.utils.format_time import TimeFormat
from typing import Callable, Literal

from functools import wraps
import asyncio, time

class Limiter:
    _instances = {}

    def __new__(cls, name:str='limiter', *args, **kwargs):
        if name not in cls._instances:
            instance = super(Limiter, cls).__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]
    
    def __init__(self, name:str='limiter'):
        """ 
        >>> # named singleton
        limiter = Limiter('limiter')
        limiter.set_rate(3, 1, 'outflow')
        xldef = limiter.wrapper(xdef,propagate=False,msg=True)

        >>> # case
        limiter = Limiter('g_mkt')._set(5,1,'outflow')

        
        """
        if not self._initialized:
            try:
                from Qlogger import Logger
                logger = Logger(name,'head')
            except ModuleNotFoundError as e:
                logger = None

            self._custom = CustomLog(logger,"Limiter",'async')
            self._custom.info.msg(name)
            self._initialized = True

    def _set(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow']):
        self.set_rate(max_worker, seconds, limit)
        return self
    

    def set_rate(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'],
                propagate=True, msg=False):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._propagate = propagate
        self._msg = msg

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg('conf', limit,f"max({max_worker})",f"sec({seconds})" )

    def wrapper(self, xdef:Callable):
        # @wraps(xdef)
        async def wrapper(*args, **kwargs):
            propagate_exception = None
            async with self._semaphore:
                if self._msg: self._custom.info.msg('start', frame=xdef.__name__)   
                try: 
                    tsp_start = time.time()     
                    result = await xdef(*args, **kwargs)
                    return result
                except Exception as e:
                    self._custom.error.msg('except',xdef.__name__,str(args),str(kwargs) )
                    propagate_exception = e
                finally:
                    tsp_finish = time.time()
                    await self.wait_reset(xdef, tsp_start, tsp_finish,msg=self._msg)
                    if propagate_exception is not None and self._propagate: #? propagate exception to retry
                        raise propagate_exception
        
        self._custom.info.msg('xdef', xdef.__name__ )
        return wrapper
    
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f"({self._semaphore._value}/{self._max_worker})"
            self._custom.info.msg('acquire',fname,self._custom.arg(f'sema{queue}',2,'l',"-") )
        elif context =="release":
            queue = f"({self._semaphore._value+1}/{self._max_worker})<"
            self._custom.info.msg('release',fname,self._custom.arg(f'sema{queue}',2,'r',"-") )

    async def wait_reset(self, xdef, tsp_start:float, tsp_finish, msg=False):

        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)
        
        if msg : self._msg_wait_reset(xdef, seconds,tsp_ref)
        if seconds > 0.0:
            await asyncio.sleep(seconds)

    def _msg_wait_reset(self, xdef, seconds:float, tsp_ref:float):
        msg_sec = TimeFormat.seconds(seconds,'hmsf')
        msg_ref = TimeFormat.timestamp(tsp_ref,'hmsf')
        self._custom.info.msg('reset',self._limit_type,msg_ref,msg_sec ,frame=xdef.__name__)


if __name__ =="__main__":
    # from Qlogger import Logger
    # logger = Logger('limiter', 'head')
    limiter = Limiter()
    limiter.set_rate(3, 1, 'outflow')

    @limiter.wrapper2
    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')

    xfunc()
    async def xerro(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        raise ValueError("raise error")
        # print(f'finish {x}')

    # xrfunc = limiter.wrapper(xfunc,propagate=False,msg=True)
    xrerro = limiter.wrapper(xerro,propagate=False,msg=False)
    
    async def main():
        tasks = []
        for _ in range(5):
            try:
                if _ == 3:
                    task = asyncio.create_task(xrerro(_),name=limiter._custom.ith() )
                else:
                    task = asyncio.create_task(xfunc(_),name=limiter._custom.ith() )
            except Exception as e:
                print(e)

        await asyncio.sleep(10)
    asyncio.run(main())


