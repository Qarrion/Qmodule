# -------------------------------- ver 240511 -------------------------------- #
# tools
# -------------------------------- ver 240527 -------------------------------- #
# limiter return
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove
# -------------------------------- ver 240609 -------------------------------- #
# kwargs limit=True

import inspect
import logging
from Qtask.utils.logger_custom import CustomLog
from Qtask.utils.format_time import TimeFormat
from typing import Callable, Literal

from functools import wraps
import asyncio, time, traceback

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
        xldef = limiter.wrapper(xdef,traceback=False,msg=True)
        xldef(limit=False)
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
        self.set_config(max_worker, seconds, limit)
        return self
    

    def set_config(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'],
                traceback=False, msg_stt=False, msg_end=False):
        
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._traceback = traceback
        self._msg_stt = msg_stt
        self._msg_end = msg_end

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg('conf', limit,f"max({max_worker})",f"sec({seconds})" )

    def wrapper(self, xdef):
        @wraps(xdef)
        async def wrapper(*args, limit=True, **kwargs):
            if limit:
                async with self._semaphore:
                    if self._msg_stt: self._custom.info.msg('start', frame=xdef.__name__)   
                    try: 
                        tsp_start = time.time()     
                        result = await xdef(*args, **kwargs)
                        return result
                    
                    except asyncio.exceptions.CancelledError as e:
                        task_name = asyncio.current_task().get_name()
                        print(f"\033[33m Interrupted ! limiter ({task_name}) \033[0m")
                        raise e

                    except Exception as e:
                        self._custom.error.msg('except',xdef.__name__,e.__class__.__name__,frame='task' )
                        raise e
                        
                    finally: # before raise e
                        tsp_finish = time.time()
                        if self._traceback: traceback.print_exc()
                        await self.wait_reset(xdef, tsp_start, tsp_finish, msg=self._msg_end)

            else:
                result = await xdef(*args, **kwargs)
                return result
        
        self._custom.info.msg('xdef', xdef.__name__ )
        return wrapper
    
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
        self._custom.info.msg('throttle',self._limit_type,msg_ref,msg_sec ,frame='task')


if __name__ =="__main__":
    # from Qlogger import Logger
    # logger = Logger('limiter', 'head')
    limiter = Limiter()
    limiter.set_config(3, 1, 'outflow')

    @limiter.wrapper
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
    xrerro = limiter.wrapper(xerro)
    
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


