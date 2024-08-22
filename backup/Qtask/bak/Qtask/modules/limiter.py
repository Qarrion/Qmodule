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

    def __new__(cls, name:str='limiter', *args, msg = True, **kwargs):
        if name not in cls._instances:
            instance = super(Limiter, cls).__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]
    
    def __init__(self, name:str='limiter', msg=True):
        """ 
        >>> # named singleton
        limiter = Limiter('limiter')
        limiter.set_rate(3, 1, 'outflow')
        xldef = limiter.wrapper(xdef,traceback=False,msg=True)
        xldef(limit=False)
        >>> # case
        limiter = Limiter('g_mkt')._set(5,1,'outflow')
        """
        CLSNAME = 'Limiter'
        if not self._initialized:
            try:
                from Qlogger import Logger
                logger = Logger(name,'head')
            except ModuleNotFoundError as e:
                logger = None
            self._initialized = True

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

    def _set(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow']):
        self.set_config(max_worker, seconds, limit)
        return self
    

    def set_config(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'],
                traceback=False, msg_run=False, msg_limit=False):
        
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._traceback = traceback
        self._msg_run = msg_run
        self._msg_limit = msg_limit

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})" )

    def wrapper(self, xdef):
        @wraps(xdef)
        async def wrapper(*args, limit=True, **kwargs):
            if limit:
                async with self._semaphore:
                    if self._msg_run: self._custom.info.msg(xdef.__name__,  str(args),'') 
                    try: 
                        tsp_start = time.time()     
                        result = await xdef(*args, **kwargs)
                        return result
                    
                    except asyncio.exceptions.CancelledError as e:
                        task_name = asyncio.current_task().get_name()
                        print(f"\033[33m Interrupted ! limiter ({task_name}) \033[0m")
                        raise e

                    except Exception as e:
                        self._custom.error.msg('except',xdef.__name__,e.__class__.__name__ )
                        raise e
                        
                    finally: # before raise e
                        tsp_finish = time.time()
                        if self._traceback: traceback.print_exc()
                        await self.wait_reset(xdef, tsp_start, tsp_finish, msg_limit=self._msg_limit)
            else:
                result = await xdef(*args, **kwargs)
                return result
        
        self._custom.info.msg( xdef.__name__ ,'','')
        return wrapper
    
    async def wait_reset(self, xdef, tsp_start:float, tsp_finish, msg_limit=False):
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)
        
        if msg_limit : 
            msg_sec = TimeFormat.seconds(seconds,'hmsf')
            # msg_ref = TimeFormat.timestamp(tsp_ref,'hmsf')
            self._custom.info.msg('limit',self._limit_type,msg_sec )

        if seconds > 0.0:
            await asyncio.sleep(seconds)


if __name__ =="__main__":
    # from Qlogger import Logger
    # logger = Logger('limiter', 'head')
    limiter = Limiter()
    # limiter.set_config(3, 1, 'outflow',msg_run=True,msg_limit=True)
    limiter.set_config(3, 1, 'outflow')

    @limiter.wrapper
    async def xfunc(x):
        print(f'start {x}')
        await asyncio.sleep(0.5)
        print(f'finish {x}')


    async def main():
        tasks = [
            asyncio.create_task(xfunc(1)),
            asyncio.create_task(xfunc(1)),
            asyncio.create_task(xfunc(1)),
            asyncio.create_task(xfunc(1)),
            asyncio.create_task(xfunc(1)),
        ]
        await asyncio.gather(*tasks)

    asyncio.run(main())



