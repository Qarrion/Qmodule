import time
import logging
import threading
from typing import Literal, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from Qrepeater.Thread.msg import Msg
from Qrepeater.timer import Timer

class Repeater:

    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.msg = Msg(logger, 'thread')
        self.timer = Timer(value, unit, logger)
        self.stop_event = threading.Event()
        self.jobs = list()
    
    def register(self, func:Callable, *args):
        if args:
            self.jobs.append(partial(func,*args))
        else:
            self.jobs.append(func)

    def start_with_thread(self):
        executor = ThreadPoolExecutor(len(self.jobs), 'worker')
        
        try:
            while not self.stop_event.wait(self.timer.remaining_seconds()):
                futures = [executor.submit(job) for job in self.jobs]

        except KeyboardInterrupt:
            print('Keyboard Interrupted!')

        finally:
            self.stop_event.set()
            executor.shutdown(wait=True)
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)



if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test','level')
    logger2 = Logger('func','level')
    repeater = Repeater(5, 'second', logger)

    def myfunc1(x):
        logger2.info(f'myfunc1 return {x}')

    def myfunc2(x):
        logger2.info(f'myfunc2 return {x}')

    from functools import partial
    
    repeater.register(myfunc1, 1)
    repeater.register(myfunc2, 2)
    # print(.total_seconds())

    repeater.start_with_thread()