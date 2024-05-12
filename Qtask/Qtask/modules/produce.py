from Qtask.tools.timer import Timer
from Qtask.tools.nowst import Nowst
from typing import Literal, Callable, List, Iterable
import asyncio
from Qtask.tools.taskq import TaskQue
from Qtask.utils.logger_custom import CustomLog

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
    p_work = Produce(logger)
    p_work.set_timer('minute_at_seconds',10)
    p_work.set_producer([work1, work2])
    await p_work.produce()
    """
    
    def __init__(self, name:str='produce', init_offset=False):
        
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Produce',name)
        self._timer = Timer(logger)
        self._nowst = Nowst(logger, init_offset = init_offset)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)
        
        self._producer={}   # produce queue in taskqueue 

        self.taskque = None
        self.timer=None

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    # ------------------------------------------------------------------------ #
    #                                synchronize                               #
    # ------------------------------------------------------------------------ #
    def get_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        """ get timer preset"""
        return self._timer.wrapper(every,at,tz,msg)

    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        self.timer = self.get_timer(every,at,tz,msg)

    # ------------------------------------------------------------------------ #
    #                                  preset                                  #
    # ------------------------------------------------------------------------ #
    def set_preset(self, preset:Literal['xsync_time','msg_divider']):
        """
        + xsync_time  : synchronize offset at Core.offset
        + msg_divider : print divider for debug
        """
        _preset = getattr(self,"work_"+preset)
        self.set_producer(_preset)

        if preset == 'xsync_time':
            self._nowst.sync_offset(False)

    # -------------------------------- divider ------------------------------- #
    async def work_msg_divider(self):
        """+ print divider"""
        self._timer._dev_divider(offset=Core.offset)
    # ------------------------------- synctime ------------------------------- #
    async def work_xsync_time(self):
        """+ synchronize offset"""
        await self._nowst.xsync_offset()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    #                                  TaskQue                                 #
    # ------------------------------------------------------------------------ #

    # def set_taskque(self, name:str):
    #     self._custom.info.msg('tools',name)
    #     self.taskque = TaskQue(name)

    # async def xput_taskque(self, fname:str, args:tuple=(), kwargs:dict=None,
    #                   timeout:int=None, retry:int=0, msg=True):
    #     """>>> # wrapper (taskq.xput_queue)"""

    #     await self.taskque.xput_queue(fname, args, kwargs, timeout, retry, msg=False)
    #     text = f"f='{fname}' a={args}, k={kwargs} t={timeout} r={retry}"
    #     if msg: self._custom.info.msg('xput',text, frame = self.taskque._frame)

    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    #                                 Produce                                  #
    # ------------------------------------------------------------------------ #

    def set_producer(self, async_def:Callable, fname:str=None):
        """queue maker"""
        if fname is None : fname = async_def.__name__ 
        self._producer[fname] = async_def
        self._custom.info.msg('xdef', fname)

    async def xproduce(self, async_defs:Callable=None, timeout=None, msg=True):
        """Run a loop that executes a function according to a timer"""
        if async_defs is not None: self.set_producer(async_defs)

        if self.timer is None: 
            print(f"\033[31m [Warning in 'produce()'] timer has not been set! \033[0m")
        if not self._producer:  
            print(f"\033[31m [Warning in 'produce()'] tasks has not been set! \033[0m")

        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm, msg = False)
            for tname,tfunc in self._producer.items():
                if timeout is None: timeout = 50
                asyncio.create_task(self._await_with_timeout(tfunc,timeout,msg=msg))
            await self._xadjust_offset(tgt_dtm, msg = False)

    async def _xadjust_offset(self, tgt_dtm, msg=False):
        await self._nowst.xadjust_offset_change(tgt_dtm, msg)

    async def _await_with_timeout(self, async_def:Callable, timeout:int, msg = False):
        try:
            if msg : self._custom.info.msg('task', self._custom.arg(async_def.__name__,3,'l',"-"), frame='produce', offset=Core.offset)
            await asyncio.wait_for(async_def(), timeout)
            if msg : self._custom.info.msg('task', self._custom.arg(async_def.__name__,3,'r',"-"), frame='produce', offset=Core.offset)

        except asyncio.TimeoutError:
            print(f'Timeout!')

        except Exception as e:
            print(str(e))
            print(e.__class__.__name__)
    # ------------------------------------------------------------------------ #

if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #

    # async def work1():
    #     print('worker1 start')
    #     await asyncio.sleep(1)
    #     print('worker1 end')

    # async def work2():
    #     print('worker2 start')
    #     await asyncio.sleep(1)
    #     print('worker2 end')

    # prod =  Produce('prod')
    # prod.set_taskque('taskq')
    # ------------------------------------------------------------------------ #
    #                                 sync test                                #
    # ------------------------------------------------------------------------ #
    p_sync = Produce('p_sync')
    p_sync.set_timer('minute_at_seconds', 55, msg=False)
    p_sync.set_preset('xsync_time')

    p_divr = Produce('p_divr')
    p_divr.set_timer('minute_at_seconds', 0, msg=False)
    p_divr.set_preset('msg_divider')
    
    p_work = Produce('p_work')
    p_work.set_timer('minute_at_seconds', 10)
    p_work.set_taskque('taskq')


    async def work1():
        # print('worker1 start')
        # await p_work.taskque.xenqueue('myfunc', args=(1,),msg=True)
        await p_work.xput_taskque('myfunc', args=(1,),msg=True)
        # print('worker1 end')

    p_work.set_producer(work1)
    # p_work.set_producer(work2)

    async def produce():
        task1 = asyncio.create_task(p_sync.xproduce(msg=False))
        task2 = asyncio.create_task(p_divr.xproduce(msg=False))
        task3 = asyncio.create_task(p_work.xproduce())

        await asyncio.gather(task1, task2, task3)

    asyncio.run(produce())


    # ------------------------------------------------------------------------ #
    #                                  warning                                 #
    # ------------------------------------------------------------------------ #

    # async def warning():
    #     p_warn =  Produce('p_warn')
    #     p_warn.set_preset('msg_divider')
    #     task = asyncio.create_task(p_warn.produce(msg=False))
    #     await asyncio.gather(task)

    # asyncio.run(warning())

    