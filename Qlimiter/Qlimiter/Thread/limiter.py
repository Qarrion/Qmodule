import logging
import threading
import time

from queue import Queue, Empty
from typing import Callable, Literal
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed

from Qlimiter.Thread import CustomMsg
from Qlimiter.Thread import Task


class Limiter:
    def __init__(self, max_calls: int, seconds: float, 
                 limit:Literal['inflow', 'outflow'], 
                 logger: logging.Logger = None):
        self.task = Task(max_calls, seconds, limit, logger)

        self.msg = CustomMsg(logger, 'thread')
        self.msg.info.strm_initiate(max_calls, seconds)

        self._max_calls = max_calls
        self._stop_event = threading.Event()
        
    # -------------------------------- worker -------------------------------- #
    def start(self):
        self.msg.debug.strm_workerpool('start')
        self.executor = ThreadPoolExecutor(max_workers=self._max_calls, thread_name_prefix="worker")
        self.futures = [self.executor.submit(self._worker) for _ in range(self._max_calls)]

    def interrupt(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Keyboard Interrupted!')
            self._stop_event.set()
            self.executor.shutdown(wait=True)
        print("WorkerPool Quit!")


    def result(self):
        for future in as_completed(self.futures):
            try:
                future.result()
            except Exception as e:
                print(e)

    def _worker(self):
        self.msg.debug.strm_worker('start')
        while not self._stop_event.is_set():
            try :
                fname, args, kwargs = self.task.func_queue.get(timeout=1)
                self.task.func_queue.task_done()
                assert fname in self.task.func_dict.keys(), 'no fname'
                self.task.func_dict[fname](*args,**kwargs)
                
            except Empty as e:
                continue
        print("a worker quit")


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

    limiter.task.register(myfunc1)
    limiter.task.register(myfunc2)


    limiter.task.func_dict['myfunc1'](1)
    limiter.task.func_dict['myfunc2'](1)
    # limiter.start()

    # limiter.task.enqueue('myfunc1',0.1)
    # limiter.task.enqueue('myfunc1',0.1)
    # limiter.task.enqueue('myfunc2',0.1)
    # limiter.task.enqueue('myfunc1',0.1)
    # limiter.task.enqueue('myfunc1',0.1)
    # limiter.task.enqueue('myfunc1',0.1)
    # limiter.task.enqueue('myfunc1',0.1)

    # limiter.interrupt()
