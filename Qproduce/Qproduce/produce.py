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
    p_worker.set_xdefs([work1, work2])
    await p_worker.produce()
    """
    def __init__(self, logger:logging.Logger = None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Produce')
        self._timer = Timer(logger)
        self._nowst = Nowst(logger, init_offset= False)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)

        # self.msg_divider()
        self.timer=None
        self.xdefs=None

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
    def set_xdefs(self, async_defs:List[Callable]):
        if isinstance(async_defs, Callable):
            async_defs = [async_defs]
            
        self.xdefs = async_defs

    def set_preset(self, preset:Literal['xsync_time','msg_divider']):
        """
        + xsync_time  : synchronize offset at Core.offset
        + msg_divider : print divider for debug
        """
        _preset = getattr(self,"work_"+preset)
        self.set_xdefs(_preset)
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

    async def produce(self, async_defs:List[Callable]=None, timeout=None, msg=True):
        """Run a loop that executes a function according to a timer"""

        if async_defs is not None: self.set_xdefs(async_defs)

        xdefs = self.xdefs
        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm,msg)
            for xdef in xdefs:
                if timeout is None: timeout = 50
                if msg : self._custom.msg('task', xdef.__name__, frame='produce', offset=Core.offset)
                asyncio.create_task(self._await_with_timeout(xdef,timeout))
            await self._xadjust_offset(tgt_dtm,msg)

    async def _xadjust_offset(self, tgt_dtm, msg=True):
        await self._nowst.xadjust_offset_change(tgt_dtm, msg)

    async def _await_with_timeout(self, async_def:Callable, timeout:int):
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
    p_worker.set_xdefs([work1, work2])


    async def produce():
        task1 = asyncio.create_task(p_xsynctime.produce())
        task2 = asyncio.create_task(p_divider.produce())
        task3 = asyncio.create_task(p_worker.produce())

        await asyncio.gather(task1, task2, task3)

    asyncio.run(produce())

