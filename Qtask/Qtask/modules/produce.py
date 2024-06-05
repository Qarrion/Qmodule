# -------------------------------- ver 240526 -------------------------------- #
# interrupt
import re
from Qtask.tools.timer import Timer
from Qtask.tools.nowst import Nowst
from typing import Literal, Callable, List, Iterable
import asyncio

from Qtask.modules.channel import Channel
from Qtask.utils.logger_custom import CustomLog

class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'Produce'

class Produce:
    """
    >>> # produce 
    prod = Produce()
    prod.set_timer('every_seconds', 2)

    >>> # ------------------------------- producer ------------------------------- #
    async def prod_task1():
        await prod.xput_channel(args=(1,2))
        print('put')

    ch01 = Channel()
    prod.set_xproducer(prod_task1,ch01,msg=True)

    async def main():
        task1 = asyncio.create_task(prod.xproduce(msg=True))
        await asyncio.gather(task1)
    asyncio.run(main())
    """    

    def __init__(self, name:str='produce', init_offset=False, msg=True):
        CLSNAME = 'Produce'
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.msg(name)
        self._timer = Timer(logger,CLSNAME)
        self._nowst = Nowst(logger,CLSNAME, init_offset = init_offset)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)
        
        self._channel:Channel = None
        self._producer = None

        self._is_msg_channel = False

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
        self.set_xproducer(_preset)

        if preset == 'xsync_time':
            self._nowst.sync_offset(True)

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
    #                                 Produce                                  #
    # ------------------------------------------------------------------------ #
    def set_channel(self, channel:Channel):
        self._channel = channel

    def set_xproducer(self, xdef:Callable, channel:Channel=None, msg=False):
        """
        + arg 'channel' object should be assigned in the 'set_xproducer' or 'set_channel'
        + msg for | xput_queue....item | """
        self._is_msg_channel = msg
        self._producer = xdef
        if channel is None:
            self._custom.info.msg('xdef', xdef.__name__, 'None')
        else:
            self._channel = channel
            self._custom.info.msg('xdef', xdef.__name__, channel._name)

    async def xput_channel(self,args:tuple=(), kwargs:dict=None, retry=0):
        """
        + args = () for no arg consumer
        + msg in set_xproducer
        """
        msg = self._is_msg_channel
        if self._channel is None:  
            print(f"\033[31m [Warning in 'xput_channel()'] 'channel' has not been set! \033[0m")
        await self._channel.xput_queue(args,kwargs,retry,msg)

    async def xproduce(self, xdef:Callable=None, timeout=None, msg=True):
        """
        + Run a loop that executes a function according to a timer
        + msg | xproduce......task |"""
        if xdef is not None: self.set_xproducer(xdef)

        if self.timer is None: 
            print(f"\033[31m [Warning in 'xproduce()'] 'timer' has not been set! \033[0m")
        if not self._producer:  
            print(f"\033[31m [Warning in 'xproduce()'] 'producer' has not been set! \033[0m")

        timer = self.timer
        while True:
            try:
                tot_sec, tgt_dtm = timer() 
                await asyncio.sleep(tot_sec)
                await self._xadjust_offset(tgt_dtm, msg = False)
                if timeout is None: timeout = 50

                asyncio.create_task(self._await_with_timeout(self._producer,timeout,msg=msg))
                await self._xadjust_offset(tgt_dtm, msg = False)
            except asyncio.exceptions.CancelledError:
                print(f"\033[33m Interrupted ! loop_xproduce ({self._producer.__name__}) \033[0m")
                break
            except Exception as e:
                print(e.__class__.__name__)
                break

    async def _xadjust_offset(self, tgt_dtm, msg=False):
        await self._nowst.xadjust_offset_change(tgt_dtm, msg)

    async def _await_with_timeout(self, xdef:Callable, timeout:int, msg = False):
        try:
            if msg : self._custom.info.msg('task', 
                    self._custom.arg(xdef.__name__,3,'l',"-"), frame='xproduce', offset=Core.offset)
            await asyncio.wait_for(xdef(), timeout)
            if msg : self._custom.info.msg('task', 
                    self._custom.arg(xdef.__name__,3,'r',"-"), frame='xproduce', offset=Core.offset)

        except asyncio.TimeoutError:
            print(f'Timeout!')

        except Exception as e:
            print(str(e))
            print(e.__class__.__name__)
    # ------------------------------------------------------------------------ #

if __name__ == "__main__":
 
    
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

    # ------------------------------------------------------------------------ #
    #                                no channel                                #
    # ------------------------------------------------------------------------ #
    # p_work = Produce('p_work')
    # p_work.set_timer('every_seconds', 10)

    # async def prod_task1():
    #     print('working')

    # p_work.set_xproducer(prod_task1)

    # async def produce():
    #     task1 = asyncio.create_task(p_work.xproduce(msg=True))
    #     await asyncio.gather(task1)

    # asyncio.run(produce())

    # ------------------------------------------------------------------------ #
    #                               with channel                               #
    # ------------------------------------------------------------------------ #
    prod = Produce('p_work')
    prod.set_timer('every_seconds', 2)

    async def prod_task1():
        await prod.xput_channel(args=(1,2))
        print('put')

    #! set channel
    ch01 = Channel()

    prod.set_xproducer(prod_task1,ch01,msg=True)

    async def produce():
        task1 = asyncio.create_task(prod.xproduce(msg=True))
        await asyncio.gather(task1)

    asyncio.run(produce())



    