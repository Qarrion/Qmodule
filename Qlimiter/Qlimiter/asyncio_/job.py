
from typing import Callable, Literal, Coroutine
import asyncio      
import logging
import time


from Qlimiter.asyncio_.msg import Msg

class Job:
    """>>> #
    job.register(func:Coroutine, name:str)
    job.enqueue(fname:str, *args, **kwargs)
    job.handler(fname:str, *args, **kwargs)
    """
    def __init__(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow'],
                 msg:Msg):
        self.msg = msg
        self._limit_type = limit
        self._max_worker = max_worker
        self._seconds = seconds

        self._semaphore = asyncio.Semaphore(max_worker)
        self.max_retry = 3
        self.registry = dict()
        self.queue = asyncio.Queue()

    def register(self,func:Coroutine, fname:str=None):
        if fname is None: fname = func.__name__
        self.msg.debug.register(self._limit_type, fname)
        self.registry[fname] = self._wrapper_throttle(func)

    async def enqueue(self, fname:str, args:tuple, retry:int=0):
        """enqueue args with function"""
        self.msg.debug.enqueue(fname, args, retry)
        await self.queue.put((fname, args, retry))

    async def dequeue(self):
        result = None
        try:
            fname, args, retry = await asyncio.wait_for(self.queue.get(), timeout=1)
            try:
                self.msg.info.dequeue(fname, args, retry)
                result = await self.registry[fname](*args) # with limit
            except Exception as e:
                if retry+1 <= self.max_retry:
                    self.msg.warning.exception('requeue',fname,args,retry)
                    await self.enqueue(fname, args, retry+1)
                else:
                    self.msg.error.exception('drop',fname,args,retry)
            finally:
                self.queue.task_done()

        except asyncio.TimeoutError:
            pass

        return result

    def _wrapper_throttle(self, func:Coroutine):
        async def wrapper(*args):
            propagate_exception = None
            msg_arg = (func.__name__, self._semaphore,self._max_worker)
            async with self._semaphore:
                self.msg.debug.semaphore("acquire", *msg_arg) 
                # ------------------------------------------------------------ #
                try: 
                    tsp_start = time.time()     
                    result = await func(*args)
                except Exception as e:
                    self.msg.error.exception('job',func.__name__, args)
                    propagate_exception = e
                # ------------------------------------------------------------ #
                finally:
                    tsp_finish = time.time()
                    await self._wait_reset(tsp_start, tsp_finish)
                    self.msg.debug.semaphore("release", *msg_arg) 
                    if propagate_exception:
                        raise propagate_exception
                    else:
                        return result
        return wrapper
    
    async def _wait_reset(self, tsp_start:float,tsp_finish):
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            self.msg.debug.wait_reset(tsp_ref,seconds,self._limit_type)
            await asyncio.sleep(seconds)
        else:
            self.msg.debug.wait_reset(tsp_ref,0,self._limit_type)

if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('job', 'level', debug=True)
    job = Job(3, 1, 'inflow', Msg(logger,'async'))

    async def myfunc(x):
        await asyncio.sleep(x)
        print(f'myfunc return {x}')

    async def myfunc_err(x):
        raise Exception ("Error raised")
    
    async def main():
        job.register(myfunc)
        job.register(myfunc_err)

        await job.enqueue('myfunc',(1,))
        await job.enqueue('myfunc_err',(1,))

        await job.dequeue()
        await job.dequeue()
        await job.dequeue()


    asyncio.run(main())