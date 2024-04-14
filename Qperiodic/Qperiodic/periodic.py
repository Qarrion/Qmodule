from backup.timer import Timer
from Qperiodic.tools.taskq import Taskq
from Qperiodic.tools.timer import Timer
from Qperiodic.tools.nowst import Nowst

import logging
from typing import Literal, Coroutine, Callable
import signal


class Periodic:

    def __init__(self, logger:logging.Logger = None):
        self.logger = logger

        self._timer = Timer(self.logger)
        self._taskq = Taskq(self.logger)
        self._newst = Nowst(self.logger)

        #! 아 이건 아닌거 같아..
        self._timer.set_core(self._newst.core())

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    def get_preset(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        """ get timer preset"""
        return self._timer.wrapper(every,at,tz,msg)

    def register_timer(self, preset:Callable, pname:str=None):
        self._timer.register(preset, pname)

    def register_taskq(self, async_def:Callable, fname:str=None):
        self._taskq.register(async_def, fname)


    def start_daemon_thread(self, pname, msg=True):
        timer = self._timer.registry[pname]
        self._newst.start_daemon_thread(timer,msg)

    def producer(self):
        pass
        
    def consumer(self):
        pass



if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    from Qlogger import Logger
    logger = Logger('test', 'green')
    from Qperiodic.tools.nowst import Nowst

    perio =  Periodic(logger)

    min_at_55_sec = perio.get_preset('minute_at_seconds',55,'KST',True)
    perio.register_timer(min_at_55_sec, 'min_at_55_sec')

    min_at_00_sec = perio.get_preset('minute_at_seconds',0,'KST',True)
    perio.register_timer(min_at_00_sec, 'min_at_00_sec')

    perio.start_daemon_thread('min_at_55_sec',msg=True)

    import time

    time.sleep(200)


    # perio.register_timer(min_at_55_sec)
    # perio.register_timer(min_at_00_sec)






    # -------------------------- start daemon thread ------------------------- #
    # nowst = Nowst(logger)
    # timer = Timer(logger)
    # timer.set_core(nowst.core())
    
    # timer_5s = timer.wrapper('every_seconds',5,msg=False)
    # nowst.start_daemon_thread(timer=timer_5s)

    # import time
    # time.sleep(20)


    # ------------------------ buffer and offset test ------------------------ #
    # timer0 = Timer(logger)

    # print(timer.minute_at_seconds(10))
    # print(timer0.minute_at_seconds(10))

    # print(timer.hour_at_minutes(10))
    # print(timer0.hour_at_minutes(10))

    # print(timer.day_at_hours(10))
    # print(timer0.day_at_hours(10))

    # print(timer.every_seconds(10))
    # print(timer0.every_seconds(10))

    # print(timer.every_minutes(10))
    # print(timer0.every_minutes(10))

    # print(timer.every_hours(10))
    # print(timer0.every_hours(10))
