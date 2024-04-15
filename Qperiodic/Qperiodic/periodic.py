import asyncio
from backup.timer import Timer
from Qperiodic.tools.taskq import Taskq
from Qperiodic.tools.timer import Timer
from Qperiodic.tools.nowst import Nowst

import logging
from typing import Literal, Coroutine, Callable, List
import signal


class Periodic:
    """ >>> #
    periodic = Periodic()
    # get timer preset
    timer_every_5s = periodic.get_timer('every_seconds',5,'KST',False)
    # register timer
    periodic.register_timer(timer_every_5s, 'timer_every_5s')
    # daemon thread
    periodic.start_daemon_thread('timer_every_5s')
    """
    def __init__(self, logger:logging.Logger = None):
        self.logger = logger

        self._timer = Timer(self.logger)
        self._taskq = Taskq(self.logger)
        self._newst = Nowst(self.logger)

        self._timer.set_core(self._newst.core)

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    def _dev_now_naive(self):
        self._newst.now_naive(msg=True)
        # self._newst.now_stamp(msg=True)
    # ------------------------------------------------------------------------ #
    #                                synchronize                               #
    # ------------------------------------------------------------------------ #
    def get_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        """ get timer preset"""
        return self._timer.wrapper(every,at,tz,msg)

    def start_daemon_thread(self, timer:Callable, msg=True):
        self._newst.start_daemon_thread(timer,msg)

    # ------------------------------------------------------------------------ #
    #                                 periodic                                 #
    # ------------------------------------------------------------------------ #
    # def register_taskq(self, async_def:Callable, fname:str=None):
    #     self._taskq.register(async_def, fname)

    # 비교적 간단한 일을 실행하기 위한 queue를 생성하는 작업을 담당함 
    # return none
    async def producer(self, timer:Callable, async_defs:List[Callable], timeout=None):
        while True:
            await asyncio.sleep(timer())
            for async_def in async_defs:
                if timeout is None:
                    asyncio.create_task(async_def())
                else :
                    asyncio.create_task(self.await_with_timeout(async_def,timeout))

    async def await_with_timeout(self, async_def:Callable, timeout:int):
        """work 함수에 타임아웃을 적용하는 함수. 처리 성공 시 output_queue에 결과를 추가함"""
        try:
            await asyncio.wait_for(async_def(), timeout)

        except asyncio.TimeoutError:
            print(f'Timeout!')

        except Exception as e:
            print(str(e))
            print(e.__class__.__name__)




if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    from Qlogger import Logger
    from Qperiodic.tools.nowst import Nowst

    logger_g = Logger('newst', 'green')
    logger_b = Logger('perio', 'blue')
    logger_y = Logger('work', 'yellow')

    async def work1():
        logger_y.info('worker1 start')
        await asyncio.sleep(1)
        logger_y.info('worker2 end')


    def daemon_test():
        perio =  Periodic(logger_b)
        # ----------------------------- daemon thread ---------------------------- #
        at_05_sec = perio.get_timer('minute_at_seconds',55,'KST',False)
        perio.start_daemon_thread(at_05_sec,msg=True)
        import time
        for _ in range(120):
            time.sleep(1)
            perio._dev_now_naive()

    def thread_daemon():
        perio =  Periodic(logger_b)
        # ----------------------------- daemon thread ---------------------------- #
        at_05_sec = perio.get_timer('minute_at_seconds',55,'KST',False)
        perio.start_daemon_thread(at_05_sec,msg=True)


    async def period():
        perio =  Periodic(logger_g)
        min_at_00_sec = perio.get_timer('minute_at_seconds',0,'KST',True)
        await perio.producer(min_at_00_sec,[work1])
        # producer_task = asyncio.create_task(perio.producer(min_at_00_sec,[work1]))
        # asyncio.gather(producer_task)

    def async_period():
        asyncio.run(period())

    def main():
        thread_daemon()
        async_period()


#! TODO  최소 

            

        # ------------------------------- periodic ------------------------------- #
        # min_at_00_sec = perio.get_timer('minute_at_seconds',0,'KST',True)
        # min_at_05_sec = perio.get_timer('minute_at_seconds',5,'KST',False)


        # loop = asyncio.get_event_loop()
        # loop = asyncio.new_event_loop()
        
        # producer_task = loop.create_task(perio.producer(min_at_00_sec,[work1]))
        
        # loop.run_until_complete(producer_task)
        # loop.close()


    main()
    # min_at_55_sec = perio.get_preset('minute_at_seconds',55,'KST',True)
    # perio.register_timer(min_at_55_sec, 'min_at_55_sec')

    # min_at_00_sec = perio.get_preset('minute_at_seconds',0,'KST',True)
    # perio.register_timer(min_at_00_sec, 'min_at_00_sec')





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
