
from typing import Callable, Literal
import threading
import queue
import logging
import time

from Qlimiter.thread_.msg import Msg

class Job:

    def __init__(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow'], 
                 logger:logging.Logger=None):
        self. msg = Msg(logger, 'thread')
        self. _limit = limit
        self. _max_worker = max_worker
        self. _seconds = seconds 

        self. _semaphore = threading.Semaphore(max_worker)
        self.registry = dict()
        self.queue = queue.Queue()

    def enqueue(self, fname:str, *args, **kwargs):
        self.msg.debug.strm_enqueue(fname, args, kwargs)
        self.queue.put((fname, args, kwargs))

    def register(self,func:Callable,name:str=None):
        if name is None: name = func.__name__
        self.msg.debug.strm_register(self._limit, name)
        if self._limit == 'inflow':
            self.registry[name] = self._wrapper_throttle_inflow(func)
        if self._limit == 'outflow':
            self.registry[name] = self._wrapper_throttle_outflow(func)
    
    def handler(self, fname:str, *args, **kwargs):
        self.msg.debug.strm_handler(fname, args, kwargs)
        return self.registry[fname](*args, **kwargs)
     
    def _wrapper_throttle_inflow(self, func:Callable):
        def wrapper(*args, **kwargs):
            with self._semaphore:
                self.msg.debug.strm_semaphore("acquire", func.__name__, 
                                              self._semaphore,self._max_worker) 
                tsp_start = time.time()     
                # ------------------------------------------------------------ #
                try: 
                    result = func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_job_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                self._wait_expire(tsp_ref=tsp_start)
                self.msg.debug.strm_semaphore("release", func.__name__, 
                                              self._semaphore,self._max_worker) 
            return result
        return wrapper
    
    def _wrapper_throttle_outflow(self, func:Callable):
        def wrapper(*args, **kwargs):
            with self._semaphore:
                self.msg.debug.strm_semaphore("acquire", func.__name__, 
                                              self._semaphore,self._max_worker) 
                # ------------------------------------------------------------ #
                try: 
                    result = func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_job_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                tsp_finish = time.time()     
                self._wait_expire(tsp_ref=tsp_finish)
                self.msg.debug.strm_semaphore("release", func.__name__, 
                                              self._semaphore,self._max_worker) 
            return result
        return wrapper

    def _wait_expire(self, tsp_ref:float):
        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            self.msg.debug.strm_wait_expire(tsp_ref,seconds,self._limit)
            time.sleep(seconds)
        else:
            self.msg.debug.strm_wait_expire(tsp_ref,0,self._limit)
        
if __name__ =="__main__":

    from Qlogger import Logger
    logger = Logger('job', 'level', debug=True)
    job = Job(3, 1, 'inflow', logger)

    def myfunc(x):
        time.sleep(x)
        print(f'myfunc return {x}')

    def myfunc_err(x):
        raise Exception ("Error raised")

    # register
    job.register(myfunc)
    job.register(myfunc_err)

    # enqueue
    job.enqueue('myfunc', 1)
    job.enqueue('myfunc_err', 1)

    # # handler
    job.handler('myfunc', 1)
    job.handler('myfunc_err', 1)
