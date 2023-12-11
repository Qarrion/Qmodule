import logging
import threading
import time
from queue import  Empty
from typing import Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
from Qlimiter.Thread import Msg
from Qlimiter.Thread import Job

class Limiter:
    def __init__(self, max_calls: int, seconds: float, 
                 limit:Literal['inflow', 'outflow'], 
                 logger: logging.Logger = None):
        
        self.job = Job(max_calls, seconds, limit, logger)

        self.msg = Msg(logger, 'thread')
        self.msg.info.strm_initiate(max_calls, seconds)

        self._max_calls = max_calls
        self._stop_event = threading.Event()
        
    # -------------------------------- worker -------------------------------- #
    def worker_poolexecutor(self, interrupt=True, result=True):
        self.msg.debug.strm_workerpool()
        self.executor = ThreadPoolExecutor(max_workers=self._max_calls, thread_name_prefix="Worker")
        self.futures = [self.executor.submit(self.worker) for _ in range(self._max_calls)]

        if interrupt:
            self.interrupt_loop(result=result)

    def worker(self):
        self.msg.debug.strm_worker()
        while not self._stop_event.is_set():
            try :
                fname, args, kwargs = self.job.queue.get(timeout=1)
                assert fname in self.job.registry.keys(), 'no fname'
                # self.job.registry[fname](*args,**kwargs)
                self.job.handler(fname,*args,**kwargs)
                self.job.queue.task_done()
                
            except Empty as e:
                continue
        print("a worker quit")

    def manager_sample(self, fname):
        from random import randint
        for i in range(10):
            x = randint(0,15)/10
            time.sleep(x)
            self.job.queue(fname, x)

    def interrupt_loop(self, result=True):
        """>>> # after worker_pool
        limiter.worker_pool(interrupt=False)
        ... other works ...
        limiter.interrupt_loop()
        """
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Keyboard Interrupted!')
            self._stop_event.set()
            self.executor.shutdown(wait=True)
            print("WorkerPool Quit!")
            if result:
                self.result_as_completed()

    def result_as_completed(self):
        for future in as_completed(self.futures):
            try:
                future.result()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'level', debug=True)

    # limiter = Limiter(3, 1, 'inflow', logger=logger)
    limiter = Limiter(3, 1, 'outflow', logger=logger)

    def myfunc1(x):
        time.sleep(x)

    def myfunc2(x):
        raise Exception ("raise Error")
        time.sleep(x)

    limiter.job.register(myfunc1)
    limiter.job.register(myfunc2)

    limiter.job.enqueue('myfunc1',0.1)
    limiter.job.enqueue('myfunc1',0.1)
    limiter.job.enqueue('myfunc2',0.1)
    limiter.job.enqueue('myfunc1',0.1)
    limiter.job.enqueue('myfunc1',0.1)
    limiter.job.enqueue('myfunc1',0.1)
    limiter.job.enqueue('myfunc1',0.1)

    # ------------------------------------------------------------------------ #
    # limiter.worker_pool(interrupt=False)
    # limiter.interrupt_roop()
    # ------------------------------------------------------------------------ #
    limiter.worker_poolexecutor(interrupt = True)
