# -------------------------------- ver 240526 -------------------------------- #
# interrupt
from functools import partial
import re
import traceback
from Qtask.tools.timer import Timer
from Qtask.tools.nowst import Nowst
from typing import Literal, Callable, List, Iterable
import asyncio

from Qtask.modules.channel import Channel
from Qtask.utils.logger_custom import CustomLog
from Qtask.utils.print_all_task import all_tasks
class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'Produce'

class Producer:
    """
    >>> # produce 
    prod = Produce()

    >>> # set_timer (if omitted, it will run ocne after 1 second)
    prod.set_timer('every_seconds', 2)

    >>> # ------------------------------- producer ------------------------------- #
    async def prod_task1():
        await prod.xput_channel(args=(1,2))
        print('put')

    ch01 = Channel()
    prod.set_xworker(prod_task1,ch01,msg=True)

    async def main():
        task1 = asyncio.create_task(prod.xproduce(msg=True))
        await asyncio.gather(task1)
    asyncio.run(main())
    """    
    def __init__(self, name:str='prod', offset=False, msg=True):
        CLSNAME = 'Producer'
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.msg(name)

        self._timer = Timer(logger,CLSNAME,Core)
        self._nowst = Nowst(logger,CLSNAME,Core,offset=offset)
        
        self._channel:Channel = None
        self._xworker = None

        self.timer=None

    # ------------------------------------------------------------------------ #
    #                                synchronize                               #
    # ------------------------------------------------------------------------ #
    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        self.timer = self._timer.wrapper(every,at,tz,msg)

    # ------------------------------------------------------------------------ #
    #                                  preset                                  #
    # ------------------------------------------------------------------------ #
    def set_preset(self, preset:Literal['xsync_time','msg_divider']):
        """
        + xsync_time  : synchronize offset at Core.offset
        + msg_divider : print divider for debug
        """
        _preset = getattr(self,"work_"+preset)
        self.set_xworker(_preset)

        if preset == 'xsync_time':
            self._nowst.sync_offset(True)

    # -------------------------------- divider ------------------------------- #
    async def work_msg_divider(self):
        """+ print divider"""
        self._timer._dev_divider(offset=Core.offset)
        task, group = all_tasks()
        self._custom.full(str(task))
        self._custom.full(str(group))

    # ------------------------------- synctime ------------------------------- #
    async def work_xsync_time(self):
        """+ synchronize offset"""
        await self._nowst.xsync_offset()
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    #                                 Produce                                  #
    # ------------------------------------------------------------------------ #
    def set_channel(self, channel:Channel):
        self._channel = channel
        self._custom.info.msg('inst', f"channel({channel._name})")

    def set_xworker(self, xdef:Callable, channel:Channel=None, msg_put=False):
        """
        + arg 'channel' object should be assigned in the 'set_xworker' or 'set_channel'
        + msg for | xput_queue....item | 
        """
        self._xworker = xdef
        self._msg_channel_put = msg_put

        if channel is None:
            self._custom.info.msg('xdef', f"xworker({xdef.__name__})")
        else:
            self._custom.info.msg('xdef', f"xworker({xdef.__name__})")
            self.set_channel(channel)

    def set_partial(self, func, *args, **kwargs):
        punc = partial(func, *args, **kwargs)
        punc.__name__ = func.__name__
        return punc
    
    async def xput_channel(self,args:tuple=(), kwargs:dict=None, retry=0):
        """
        + args = () for no arg consumer
        + msg in set_xworker"""
        await self._channel.xput_queue(args,kwargs,retry,msg=self._msg_channel_put)

    async def xproduce(self, timeout=10, msg_div=True, msg_adjust=False):
        """
        + Run a loop that executes a function according to a timer
        + msg | xproduce......task |"""
        if not self._xworker:  
            print(f"\033[31m [Warning in 'xproduce()'] 'xworker' has not been set! \033[0m")
            return
        
        if self._channel is None:  
            print(f"\033[31m [Warning in 'xput_channel()'] 'channel' has not been set! \033[0m")
        
        if self.timer is None: 
            print(f"\033[31m [Warning in 'xproduce()'] 'timer' has not been set! \033[0m")
            await asyncio.sleep(1)
            await asyncio.wait_for(self._xworker(), timeout=timeout)
             
        else:
            timer = self.timer
            while True:
                try:
                    tot_sec, tgt_dtm = timer() 
                    await asyncio.sleep(tot_sec)
                    await self._nowst.xadjust_offset_change(tgt_dtm, msg = msg_adjust)

                    if msg_div: self._custom.info.msg('exec', self._custom.arg(self._xworker.__name__,3,'l',"-"), offset=Core.offset)
                    await asyncio.wait_for(self._xworker(), timeout)
                    if msg_div: self._custom.info.msg('exec', self._custom.arg(self._xworker.__name__,3,'r',"-"), offset=Core.offset)

                    await self._nowst.xadjust_offset_change(tgt_dtm, msg = msg_adjust)
                except asyncio.exceptions.CancelledError:
                    print(f"\033[33m Interrupted ! loop_xproduce ({self._xworker.__name__}) \033[0m")
                    break
                except asyncio.TimeoutError:
                    print(f'Timeout!')
                except Exception as e:
                    print(e.__class__.__name__)
                    traceback.print_exc()
                    break

if __name__ == "__main__":

    ch = Channel()

    prod = Producer(offset=True)
    prod.set_timer('every_seconds', 10)

    # --------------------------------- plain -------------------------------- #
    # async def xworkeR():
    #     await prod.xput_channel(args=(1,)) 

    # prod.set_xworker(xworkeR,ch)

    # -------------------------------- partial ------------------------------- #
    async def xworkeR(x):
        await prod.xput_channel(args=(x,)) 

    xWorkeR = prod.set_partial(xworkeR,x=2)
    prod.set_xworker(xWorkeR,ch)

    async def main():
        await prod.xproduce()

    asyncio.run(main())
    # ------------------------------------------------------------------------ #
    #                                  preset                                  #
    # ------------------------------------------------------------------------ #
    # p_sync = Produce('p_sync')
    # p_sync.set_timer('every_seconds', 10)
    # p_sync.set_preset('xsync_time')
    # p_divr = Produce('p_divr')
    # p_divr.set_timer('every_seconds', 20)
    # p_divr.set_preset('msg_divider')

    # async def produce():
    #     task1 = asyncio.create_task(p_sync.xproduce(msg=False))
    #     task2 = asyncio.create_task(p_divr.xproduce(msg=False))
    #     await asyncio.gather(task1, task2)

    # asyncio.run(produce())



    