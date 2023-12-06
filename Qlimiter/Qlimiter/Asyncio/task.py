
from typing import Callable, Literal
# from asyncio import Semaphore, Queue
import asyncio      
from Qlimiter.Asyncio import CustomMsg
import logging
import time

class Task:
    def __init__(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow'],
                 logger:logging.Logger=None):
        
        self.msg = CustomMsg(logger, 'async')
        self._limit = limit
        self._max_worker = max_worker
        self._seconds = seconds
        self._semaphore = asyncio.Semaphore(max_worker)

        self.func_dict = dict()
        self.func_queue = asyncio.Queue()

    async def enqueue(self, fname:str, *args, **kwargs):
        await self.func_queue.put((fname, args, kwargs))

    def register(self,func:Callable,name:str=None):
        if name is None: name = func.__name__
        self.msg.debug.strm_register(self._limit, name)
        if self._limit == 'inflow':
            self.func_dict[name] = self._wrapper_throttle_inflow(func)
        if self._limit == 'outflow':
            self.func_dict[name] = self._wrapper_throttle_outflow(func)

    def _wrapper_throttle_inflow(self, func:Callable):
        async def wrapper(*args, **kwargs):
            async with self._semaphore:
                self.msg.debug.strm_semaphore_acquire(self._semaphore,self._max_worker) 
                tsp_start = time.time()     
                # ------------------------------------------------------------ #
                try: 
                    result = await func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_task_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                await self._wait_for_expire(tsp_ref=tsp_start)
                self.msg.debug.strm_semaphore_release(self._semaphore,self._max_worker)
            return result
        return wrapper
    
    def _wrapper_throttle_outflow(self, func:Callable):
        async def wrapper(*args, **kwargs):
            async with self._semaphore:
                self.msg.debug.strm_semaphore_acquire(self._semaphore,self._max_worker)
                # ------------------------------------------------------------ #
                try: 
                    result = await func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_task_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                tsp_finish = time.time()     
                await self._wait_for_expire(tsp_ref=tsp_finish)
                self.msg.debug.strm_semaphore_release(self._semaphore,self._max_worker)
            return result
        return wrapper
    
    async def _wait_for_expire(self, tsp_ref:float):
        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            self.msg.debug.strm_waitfor_expire(tsp_ref,seconds)
            await asyncio.sleep(seconds)
        else:
            self.msg.debug.strm_waitfor_expire(tsp_ref,0)

if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('task', 'level', debug=True)
    task = Task(3, 1, 'inflow', logger)

    async def myfunc(x):
        await asyncio.sleep(x)
        print(f'myfunc return {x}')

    async def myfunc_err(x):
        raise Exception ("Error raised")
    

    async def main():

        task.register(myfunc)
        task.register(myfunc_err)

        await task.enqueue('myfunc',0.5)
        await task.enqueue('myfunc_err',x=2)

        fname, args, kwarg = await task.func_queue.get()
        print(fname)
        print(args)
        print(kwarg)
        await task.func_dict[fname](*args, **kwarg)
        fname, args, kwarg = await task.func_queue.get()
        print(fname)
        print(args)
        print(kwarg)
        await task.func_dict[fname](*args, **kwarg)

    asyncio.run(main())