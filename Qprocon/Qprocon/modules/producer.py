from functools import partial
import traceback
from typing import Callable, Literal
from Qlogger import Logger
from Qprocon.tools.nowst import Nowst
from Qprocon.tools.timer import Timer
from Qprocon.utils.custom_print import cprint
import asyncio

from collections import namedtuple
Item = namedtuple('item', ['args', 'kwargs', 'retry'])
class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'main'
class Producer:

    def __init__(self, name:str='producer', msg=False):
        self._logger = Logger(logname=name, clsname='Producer', msg=msg, context='async')

        self.core = Core
        self._timer = Timer()
        self._nowst = Nowst()
        self._timer.set_core(Core)
        self._nowst.set_core(Core)

        self._logger.set_sublogger(self._timer._logger)
        self._logger.set_sublogger(self._nowst._logger)

        self.timer = None
        self.xworker = None
        self.queue = None

        self._msg_item = False

    def now_kst(self, msg=False):
        return self._nowst.now_kst(msg=msg)

    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        self.timer = self._timer.wrapper(every,at,tz,msg)

    def set_queue(self, queue:asyncio.Queue, msg=False):
        self.queue = queue
        if msg: self._logger.info.msg(queue._name,"","")

    def set_preset(self, preset:Literal['xsync_time','msg_divider','xput_default'],msg_xsync=True):
        """
        + xsync_time  : synchronize offset at Core.offset
        + msg_divider : print divider for debug
        """
        if preset == 'xsync_time':
            self.set_xworker(self.work_xsync_time)
            self._nowst.sync_offset(msg=msg_xsync)
        elif preset == 'msg_divider':
            self.set_xworker(self.work_msg_divider)
        elif preset == 'xput_default':
            self.set_xworker(self.xput_default_queue)


    # -------------------------------- divider ------------------------------- #
    async def work_msg_divider(self):
        """+ print divider"""
        self._logger.info.div(offset=Core.offset)

    # # ------------------------------- synctime ------------------------------- #
    async def work_xsync_time(self):
        """+ synchronize offset"""
        await self._nowst.xsync_offset(msg=True)

    # -------------------------- xput_default_queue -------------------------- #
    async def xput_default_queue(self):
        await self.xput_queue()


    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    def set_xworker(self, xdef:Callable, queue:asyncio.Queue=None, msg=False):
        """
        + arg 'channel' object should be assigned in the 'set_xworker' or 'set_channel'
        + msg for | xput_queue....item | 
        """
        self.xworker = xdef
        if msg : self._logger.info.msg(xdef.__name__,"",widths=(2,1))
        if queue is not None:
            self.set_queue(queue)

    def get_partial(self, func, *args, **kwargs):
        punc = partial(func, *args, **kwargs)
        punc.__name__ = func.__name__
        return punc

    async def xput_queue(self, args:tuple=(), kwargs:dict={}, retry:int=0):
        assert self.queue is not None
        assert isinstance(args, tuple)
        assert isinstance(kwargs, dict)
        assert isinstance(retry, int)

        item = Item(args=args, kwargs=kwargs, retry=retry)
        await self.queue.put(item=item)
        if self._msg_item: self._logger.info.msg(f"{self.xworker.__name__}()",str(item))


    # ------------------------------------------------------------------------ #
    #                                  produce                                 #
    # ------------------------------------------------------------------------ #
    async def xproduce(self, timeout=None, msg_flow=True, msg_adjust=False, msg_item=False, test=False):
        
        self._msg_item = msg_item

        if test:
            await asyncio.sleep(1)
            await asyncio.wait_for(self.xworker(), timeout=timeout)
            return 0

        assert self.timer is not None
        assert self.xworker is not None

        while True:
            try:
                tot_sec, tgt_dtm = self.timer() 
                await asyncio.sleep(tot_sec)
                await self._nowst.xadjust(tgt_dtm, msg = msg_adjust)

                if msg_flow : self._logger.info.msg(self.xworker.__name__,widths=(3,),aligns=("<"),paddings=("-"),offset=self.core.offset)
                await asyncio.wait_for(self.xworker(), timeout)
                if msg_flow : self._logger.info.msg(self.xworker.__name__,widths=(3,),aligns=(">"),paddings=("-"),offset=self.core.offset)

            except asyncio.exceptions.CancelledError:
                task_name = asyncio.current_task().get_name()
                cprint(f"Interrupted ! loop_xproduce ({task_name}) closed",'yellow_')
                break
            
            except asyncio.TimeoutError:
                print(f'Timeout!')

            except Exception as e:
                print(e.__class__.__name__)
                traceback.print_exc()
                break

if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                  preset                                  #
    # ------------------------------------------------------------------------ #
    p_sync = Producer('p_sync')
    p_sync.set_timer('every_seconds', 5)
    p_sync.set_preset('xsync_time')
    p_divr = Producer('p_divr')
    p_divr.set_timer('every_seconds', 20)
    p_divr.set_preset('msg_divider')

    p_print= Producer('p')
    p_print.set_timer('every_seconds', 6)

    async def pp():
        p_print._logger.info.msg(p_print._nowst.now_kst())

    p_print.set_xworker(pp)

    async def produce():
        task1 = asyncio.create_task(p_sync.xproduce(msg_flow=False))
        task2 = asyncio.create_task(p_divr.xproduce(msg_flow=False))
        task2 = asyncio.create_task(p_print.xproduce(msg_flow=False))
        await asyncio.gather(task1, task2)

    asyncio.run(produce())

    # ------------------------------------------------------------------------ #
    #                                  default                                 #
    # ------------------------------------------------------------------------ #
    # p_xput = Producer('p_xput')
    # p_xput.set_timer('every_seconds', 5)
    # p_xput.set_preset('xput_default')
    # p_xput.set_queue(asyncio.Queue())
    # async def produce():
    #     task1 = asyncio.create_task(p_xput.xproduce(msg_flow=False,msg_item=True))
    #     await asyncio.gather(task1)

    # asyncio.run(produce())
    # ------------------------------------------------------------------------ #
    #                                   plain                                  #
    # ------------------------------------------------------------------------ #
    # prod = Producer('prod')
    # prod.set_timer('every_seconds',5)
    
    # async def xworkeR():
    #     print("do prod")
    # prod.set_xworker(xdef=xworkeR)
    
    # async def main():
    #     task = asyncio.create_task(prod.xproduce(), name='producer')
    #     await asyncio.gather(task)
    # asyncio.run(main())

    # ------------------------------------------------------------------------ #
    #                                  partial                                 #
    # ------------------------------------------------------------------------ #
    # prod = Producer('prod')
    # prod.set_timer('every_seconds',5)
    
    # async def xworkeR(x):
    #     print(f"do prod {x}")

    # xWorkeR = prod.get_partial(xworkeR,x=2)

    # prod.set_xworker(xWorkeR)     
    
    # async def main():
    #     task = asyncio.create_task(prod.xproduce(msg_flow=True), name='producer-partial')
    #     await asyncio.gather(task)
    # asyncio.run(main())
