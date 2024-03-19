from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import threading
import logging
import time
from typing import Literal, Callable
from Qrepeater.msg import Msg
from Qrepeater.timer import Timer

class ThreadRepeater:
    """
    register func 안에 반드시 unit value 이전에 작업이 안전하게 종료 되도록 timeout 로직 필요
    timeout 은 task를 강제 종료 하지 못함, -> 루프 종료 선택
    """
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger):
        self.tracer = Msg(logger, 'thread')
        self.timer = Timer(value, unit, logger)

        self._stop_event = threading.Event()
        self._jobs = list()
    
    def register(self, func:Callable, *args):
        if args:
            self._jobs.append(partial(func,*args))
        else:
            self._jobs.append(func)

    def start_with_thread(self):
        executor = ThreadPoolExecutor(len(self._jobs), 'worker')
        
        try:
            while not self._stop_event.wait(self.timer.remaining_seconds()):
                futures = [executor.submit(job) for job in self._jobs]

                for future in as_completed(futures,timeout=4):
                    try:
                        future.result()
                    except Exception as e:      #* submit error
                        print(e)

        except TimeoutError as e:               #* timeout error
            self.tracer.error.catch(e)

        except KeyboardInterrupt as e:
            self.tracer.error.catch(e)

        finally:
            self._stop_event.set()
            executor.shutdown(wait=True)


if __name__ == "__main__":
    from Qrepeater.utils.log_color import ColorLog
    main_logger = ColorLog('func','green')
    # -------------------------------- thread -------------------------------- #
    thread_logger = ColorLog('test','blue')
    repeater = ThreadRepeater(5, 'second', thread_logger)

    def myfunc(x):
        main_logger.warning(f'myfunc{x} sleep ({x})')
        time.sleep(x)
        main_logger.warning(f'myfunc{x} done!')

    # from functools import partial
    repeater.register(myfunc, 1)
    repeater.register(myfunc, 2)
    repeater.register(myfunc, 3)
  
    repeater.start_with_thread()
