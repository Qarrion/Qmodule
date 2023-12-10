
from typing import Callable, Literal
import asyncio      
import logging
import time


from Qlimiter.Asyncio import Msg

class Job:

    def __init__(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        self.msg = Msg(logger, 'async')
        self._limit = limit
        self._max_worker = max_worker
        self._seconds = seconds

        self._semaphore = asyncio.Semaphore(max_worker)
        self.registry = dict()
        self.queue = asyncio.Queue()

    async def enqueue_coro(self, fname:str, *args, **kwargs):
        self.msg.debug.strm_enqueue(fname, args, kwargs)
        await self.queue.put((fname, args, kwargs))

    def register_sync(self,func:Callable, name:str=None):
        if name is None: name = func.__name__
        self.msg.debug.strm_register(self._limit, name)
        if self._limit == 'inflow':
            self.registry[name] = self._wrapper_throttle_inflow(func)
        if self._limit == 'outflow':
            self.registry[name] = self._wrapper_throttle_outflow(func)

    async def handler(self, fname:str, *args, **kwargs):
        self.msg.debug.strm_handler(fname, args, kwargs)
        result = await self.registry[fname](*args, **kwargs)
        return result
    
    def _wrapper_throttle_inflow(self, func:Callable):
        async def wrapper(*args, **kwargs):
            async with self._semaphore:
                self.msg.debug.strm_semaphore("acquire", func.__name__, 
                                              self._semaphore,self._max_worker) 
                tsp_start = time.time()     
                # ------------------------------------------------------------ #
                try: 
                    result = await func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_job_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                await self._wait_expire(tsp_ref=tsp_start)
                self.msg.debug.strm_semaphore("release", func.__name__, 
                                              self._semaphore,self._max_worker) 
            return result
        return wrapper
    
    def _wrapper_throttle_outflow(self, func:Callable):
        async def wrapper(*args, **kwargs):
            async with self._semaphore:
                self.msg.debug.strm_semaphore("acquire", func.__name__, 
                                              self._semaphore,self._max_worker) 
                # ------------------------------------------------------------ #
                try: 
                    result = await func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_job_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                tsp_finish = time.time()     
                await self._wait_expire(tsp_ref=tsp_finish)
                self.msg.debug.strm_semaphore("release", func.__name__, 
                                              self._semaphore,self._max_worker) 
            return result
        return wrapper
    
    async def _wait_expire(self, tsp_ref:float):
        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            self.msg.debug.strm_wait_expire(tsp_ref,seconds,self._limit)
            await asyncio.sleep(seconds)
        else:
            self.msg.debug.strm_wait_expire(tsp_ref,0,self._limit)

if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('job', 'level', debug=True)
    job = Job(3, 1, 'inflow', logger)

    async def myfunc(x):
        await asyncio.sleep(x)
        print(f'myfunc return {x}')

    async def myfunc_err(x):
        raise Exception ("Error raised")
    

    async def main():
        # register
        job.register_sync(myfunc)
        job.register_sync(myfunc_err)

        await job.enqueue_coro('myfunc',1)
        await job.enqueue_coro('myfunc_err',1)

        await job.handler('myfunc',1)
        await job.handler('myfunc_err',1)

    asyncio.run(main())