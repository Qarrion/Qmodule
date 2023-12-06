
from typing import Callable, Literal
# from threading import Semaphore
import threading
import queue
# from queue import Queue
import logging
import time

from Qlimiter.Thread import CustomMsg

class Task:

    def __init__(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow'], 
                 logger:logging.Logger=None):
        self. msg = CustomMsg(logger, 'thread')
        self. _limit = limit
        self. _max_worker = max_worker
        self. _seconds = seconds 
        self. _semaphore = threading.Semaphore(max_worker)

        self.func_dict = dict()
        self.func_queue = queue.Queue()

    def enqueue(self, fname:str, *args, **kwargs):
        # self.msg.debug.strm_enqueue(fname, args, kwargs)
        self.func_queue.put((fname, args, kwargs))

    def register(self,func:Callable,name:str=None):
        if name is None: name = func.__name__
        self.msg.debug.strm_register(self._limit, name)
        if self._limit == 'inflow':
            self.func_dict[name] = self._wrapper_throttle_inflow(func)
        if self._limit == 'outflow':
            self.func_dict[name] = self._wrapper_throttle_outflow(func)
    
    def _wrapper_throttle_inflow(self, func:Callable):
        def wrapper(*args, **kwargs):
            with self._semaphore:
                self.msg.debug.strm_semaphore_acquire(self._semaphore,self._max_worker) 
                tsp_start = time.time()     
                # ------------------------------------------------------------ #
                try: 
                    result = func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_task_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                self._wait_for_expire(tsp_ref=tsp_start)
                self.msg.debug.strm_semaphore_release(self._semaphore,self._max_worker)
            return result
        return wrapper
    
    def _wrapper_throttle_outflow(self, func:Callable):
        def wrapper(*args, **kwargs):
            with self._semaphore:
                self.msg.debug.strm_semaphore_acquire(self._semaphore,self._max_worker)
                # ------------------------------------------------------------ #
                try: 
                    result = func(*args, **kwargs)
                except Exception as e:
                    self.msg.error.strm_task_error(func.__name__, args, kwargs)
                    result = False
                # ------------------------------------------------------------ #
                tsp_finish = time.time()     
                self._wait_for_expire(tsp_ref=tsp_finish)
                self.msg.debug.strm_semaphore_release(self._semaphore,self._max_worker)
            return result
        return wrapper

    def _wait_for_expire(self, tsp_ref:float):
        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            self.msg.debug.strm_waitfor_expire(tsp_ref,seconds)
            time.sleep(seconds)
        else:
            self.msg.debug.strm_waitfor_expire(tsp_ref,0)
        
if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('task', 'level', debug=True)
    task = Task(3, 1, 'inflow', logger)

    def myfunc(x):
        time.sleep(x)
        print(f'myfunc return {x}')

    def myfunc_err(x):
        raise Exception ("Error raised")


    # register
    task.register(myfunc)
    task.register(myfunc_err)

    # task.func_dict['myfunc'](1)

    # ------------------------------------------------------------------------ #
    # import threading
    # threading.Thread(target=task.func_dict['myfunc'], args=(1,)).start()
    # time.sleep(0.1)
    # threading.Thread(target=task.func_dict['myfunc'], args=(1,)).start()
    # time.sleep(0.1)
    # threading.Thread(target=task.func_dict['myfunc_err'], args=(1,)).start()
    # time.sleep(0.1)

    # ------------------------------------------------------------------------ #
    task.enqueue('myfunc',1)
    task.enqueue('myfunc_err',x=2)

    fname, args, kwarg = task.func_queue.get()
    print(fname)
    print(args)
    print(kwarg)
    task.func_dict[fname](*args, **kwarg)

    fname, args, kwarg = task.func_queue.get()
    print(fname)
    print(args)
    print(kwarg)
    task.func_dict[fname](*args, **kwarg)
