from Qproduce.tools.timer import Timer
from Qproduce.tools.nowst import Nowst
from typing import Literal, Callable, List, Iterable
import logging, asyncio

from Qproduce.utils.logger_custom import CustomLog

class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'Produce'

class Produce:
    """ + server time = local time + Core.offset
    
    >>> # basic
    prod = Produce(logger)
    at_05_sec = prod.get_timer('minute_at_seconds',55,'KST',True)

    >>> # synchronize offset
    p_xsynctime = Produce(logger)
    p_xsynctime.set_timer('minute_at_seconds',55)
    p_xsynctime.set_preset('xsync_time')
    await prod1.produce()

    >>> # peridoic divider
    p_divider = Produce(logger)
    p_divider.set_timer('minute_at_seconds',0)
    p_divider.set_preset('msg_divider')
    await prod.produce()

    >>> # prod loop_task
    p_worker = Produce(logger)
    p_worker.set_timer('minute_at_seconds',10)
    p_worker.set_task([work1, work2])
    await p_worker.produce()
    """
    def __init__(self, logger:logging.Logger = None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Produce')
        self._timer = Timer(logger)
        self._nowst = Nowst(logger, init_offset= False)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)

        self._tasks={}
        # self.msg_divider()
        self.timer=None

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    # ------------------------------------------------------------------------ #
    #                                synchronize                               #
    # ------------------------------------------------------------------------ #
    def get_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        """ get timer preset"""
        return self._timer.wrapper(every,at,tz,msg)

    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        self.timer = self.get_timer(every,at,tz,msg)

    # ------------------------------------------------------------------------ #
    #                                  common                                  #
    # ------------------------------------------------------------------------ #
    def set_task(self, async_def:Callable, fname:str=None):
        if fname is None : fname = async_def.__name__ 
        self._tasks[fname] = async_def


    def set_preset(self, preset:Literal['xsync_time','msg_divider']):
        """
        + xsync_time  : synchronize offset at Core.offset
        + msg_divider : print divider for debug
        """
        _preset = getattr(self,"work_"+preset)
        self.set_task(_preset)
    # ------------------------------------------------------------------------ #
    #                                 Produce                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- divider ------------------------------- #
    async def work_msg_divider(self):
        """+ print divider"""
        self._timer._dev_divider(offset=Core.offset)

    async def work_xsync_time(self):
        """+ synchronize offset"""
        await self._nowst.xsync_offset()
    # ------------------------------- producer ------------------------------- #

    async def produce(self, async_defs:Callable=None, timeout=None, msg=True):
        """Run a loop that executes a function according to a timer"""

        if async_defs is not None: self.set_task(async_defs)
        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm, msg = False)
            for tname,tfunc in self._tasks.items():
                if timeout is None: timeout = 50
                # if msg : self._custom.msg('task', self._custom.arg(tname,3,'l',"-"), frame='produce', offset=Core.offset)
                asyncio.create_task(self._await_with_timeout(tfunc,timeout,msg=msg))
            await self._xadjust_offset(tgt_dtm, msg = False)

    async def _xadjust_offset(self, tgt_dtm, msg=False):
        await self._nowst.xadjust_offset_change(tgt_dtm, msg)

    async def _await_with_timeout(self, async_def:Callable, timeout:int, msg = False):
        try:
            if msg : self._custom.msg('task', self._custom.arg(async_def.__name__,3,'l',"-"), frame='produce', offset=Core.offset)
            await asyncio.wait_for(async_def(), timeout)
            if msg : self._custom.msg('task', self._custom.arg(async_def.__name__,3,'r',"-"), frame='produce', offset=Core.offset)

        except asyncio.TimeoutError:
            print(f'Timeout!')

        except Exception as e:
            print(str(e))
            print(e.__class__.__name__)


if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    from Qproduce.utils.logger_color import ColorLog
    log_blue = ColorLog('prod', 'blue')
    # log_green = ColorLog('prod', 'green')
    logger_y = ColorLog('work', 'yellow')

    async def work1():
        logger_y.info('worker1 start')
        await asyncio.sleep(1)
        logger_y.info('worker1 end')

    async def work2():
        logger_y.info('worker2 start')
        await asyncio.sleep(1)
        logger_y.info('worker2 end')
    
    # ------------------------------------------------------------------------ #
    #                                 sync test                                #
    # ------------------------------------------------------------------------ #
    p_xsynctime =  Produce(log_blue)
    p_xsynctime.set_timer('minute_at_seconds',55, msg=False)
    p_xsynctime.set_preset('xsync_time')

    p_divider =  Produce(log_blue)
    p_divider.set_timer('minute_at_seconds',0,msg=False)
    p_divider.set_preset('msg_divider')
    
    p_worker =  Produce(log_blue)
    p_worker.set_timer('minute_at_seconds',10)
    p_worker.set_task(work1)
    p_worker.set_task(work2)


    async def produce():
        task1 = asyncio.create_task(p_xsynctime.produce())
        task2 = asyncio.create_task(p_divider.produce())
        task3 = asyncio.create_task(p_worker.produce())

        await asyncio.gather(task1, task2, task3)

    asyncio.run(produce())

