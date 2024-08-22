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
                    if self._msg_run: self._custom.info.msg(xdef.__name__) 
                    try: 
                        tsp_start = time.time()     
                        result = await xdef(*args, **kwargs)
                        return result
                    
                    except asyncio.exceptions.CancelledError as e:
                        task_name = asyncio.current_task().get_name()
                        print(f"\033[33m Interrupted ! limiter ({task_name}) \033[0m")

                    except Exception as e:
                        self._custom.error.msg(xdef.__name__,'except',e.__class__.__name__ )
                        if self._traceback: traceback.print_exc()
                        raise e
                        
                    finally:
                        tsp_finish = time.time()
                        await self.wait_reset(tsp_start, tsp_finish, msg_limit=self._msg_limit)
            else:
                result = await xdef(*args, **kwargs)
                return result
        
        self._custom.info.msg( xdef.__name__ ,'','')
        return wrapper
    
    async def wait_reset(self, tsp_start:float, tsp_finish, msg_limit=False):
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
            self._custom.info.msg('limit',self._limit_type, msg_sec)

        if seconds > 0.0:
            await asyncio.sleep(seconds)

    async def safe(self):
        await asyncio.sleep(0.2)
        active = 0
        for _ in range(self._max_worker):
            await self._semaphore.acquire()
            active += 1
            print(active)

        await asyncio.sleep(1)
        print('do someThing')

        for _ in range(self._max_worker):
            self._semaphore.release()
            active -= 1
            print(active)


#TODO  httpx 와 asyncpool을 이용해서 안전하게 restart 까지
# async def safe(self): 활용
# https://www.psycopg.org/psycopg3/docs/advanced/pool.html#connection-pools
# https://www.psycopg.org/psycopg3/docs/advanced/async.html
# httpx는 내부적으로 풀이용 
# psycopg 는 connection-pools 써야 
# restart에 신경쓰고
# fetch는 limiter
# balancer는 throw에 쓸까함

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


    async def loop():
        while True:
            tasks = [
            asyncio.create_task(xfunc(1)),
            asyncio.create_task(xfunc(2)),
            asyncio.create_task(xfunc(3)),
            asyncio.create_task(xfunc(4))
            ]
            await asyncio.gather(* tasks)

    async def main():
        tasks = [
            asyncio.create_task(loop()),
            asyncio.create_task(limiter.safe())
        ]
        await asyncio.gather(* tasks)



    asyncio.run(main())





    # ----------------------------- error control ---------------------------- #
    # @limiter.wrapper
    # async def xfunc(x):
    #     print(f'start {x}')
    #     await asyncio.sleep(0.5)
    #     print(f'finish {x}')
    # @limiter.wrapper
    # async def xerror(x):
    #     print(f'start {x}')
    #     await asyncio.sleep(0.5)
    #     raise ValueError
    #     print(f'finish {x}')


    # async def main():
    #     tasks = [
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1)),
    #         asyncio.create_task(xerror(1)),
    #         asyncio.create_task(xfunc(1)),
    #         asyncio.create_task(xfunc(1)),
    #     ]
    #     await asyncio.gather(*tasks)

    # asyncio.run(main())



