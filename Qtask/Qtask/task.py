# -------------------------------- ver 240521 -------------------------------- #
# set_channel
from re import T
from typing import Callable, Literal

from Qtask.modules.produce import Produce
from Qtask.modules.consume import Consume
from Qtask.modules.channel import Channel
from Qtask.modules.limiter import Limiter
from Qtask.modules.balance import Balance
from Qtask.utils.logger_custom import CustomLog
import asyncio
class xdebug:

    @classmethod
    async def monitor(self, sec:int=1):
        try:
            while True:
                await asyncio.sleep(sec)
            # print('1')
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! Interrupted !! \033[0m")

    @classmethod
    async def gather(self, tasks:list):
        try:
            await asyncio.gather(*tasks)
            # print('1')
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! all task closed !! \033[0m")

        except Exception as e:
            print(e.__class__.__name__)


class Task:

    def __init__(self,name:str='Task'):
        """
        + each instance shares same channel 
        + all instance shares offset (in produce)
        """
        try:    
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg("Task",name)
        
        self.channel = Channel(name,msg=False)
        self.consume = Consume(name,msg=False)
        self.produce = Produce(name,msg=False)

        self.consume.set_channel(self.channel)
        self.produce.set_channel(self.channel)

    # ------------------------------------------------------------------------ #
    #                                   util                                   #
    # ------------------------------------------------------------------------ #
    def sync_offset(self):
        self.produce._nowst.sync_offset()

    def now_naive(self,msg=False):
        return self.produce._nowst.now_naive(msg=msg)

    # ------------------------------------------------------------------------ #
    #                                   prod                                   #
    # ------------------------------------------------------------------------ #
    def set_timer(self,
            every: Literal['minute_at_seconds', 'hour_at_minutes', 'day_at_hours',
                                    'every_seconds', 'every_minutes', 'every_hours'], 
            at: float = 5, tz: Literal['KST', 'UTC'] = 'KST', msg: bool = False):
        """+ timer on producer or preset"""
        self.produce.set_timer(every=every,at=at,tz=tz,msg=msg)

    def set_preset(self,preset: Literal['xsync_time', 'msg_divider']):
        """+ produce preset"""
        self.produce.set_preset(preset=preset)

    def set_xproducer(self,xdef:Callable=None, msg=False):
        """+ produce
        + if xdef is none then default without arguments producer
        + msg for | xput_queue....item |
        >>>  # producer
        xput_channel(args=(),kwargs=None,retry=0)
        """
        # channel = self.channel
        if xdef is None:
            self.produce.set_xproducer(xdef=self.xproducer, channel=None, msg=msg)
        else:
            self.produce.set_xproducer(xdef=xdef, channel=None,msg=msg)

    async def xput_channel(self,args:tuple=(), kwargs:dict=None, retry= 0):
        """ 
        + in xproduce custom xdef -> set_producer(xdef)
        + args = () for no arg consumer"""
        await self.produce.xput_channel(args,kwargs,retry)

    async def xrun_xproduce(self,xdef:Callable=None,timeout=None,msg=True):
        await self.produce.xproduce(xdef=xdef,timeout=timeout,msg=msg)

    async def xproducer(self):
        """default without arguments producer"""
        await self.xput_channel()
    # ------------------------------------------------------------------------ #
    #                                   cons                                   #
    # ------------------------------------------------------------------------ #
    def set_xconsumer(self,xdef:Callable,msg_get = False, msg_put = False, msg_run = False):
        self.consume.set_xconsumer(xdef=xdef, channel=None,
                                   msg_get=msg_get,msg_put=msg_put,msg_run=msg_run)

    async def xrun_xconsume(self,timeout:int=None, maxtry:int=3, msg=False):
        await self.consume.xconsume(timeout=timeout, maxtry=maxtry, msg=msg)



if __name__ == "__main__":

    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    import asyncio

    t_task = Task('worker')
    t_task.set_timer('minute_at_seconds',10,'KST')
    
    async def pub():
        for i in range(10):
            await t_task.xput_channel(args=(i/10,))

    t_task.set_xproducer(pub)

    async def sub(sec):
        await asyncio.sleep(sec)

    t_task.set_xconsumer(sub)

    async def main():
        p_task = asyncio.create_task(t_task.xrun_xproduce())
        c_task = asyncio.create_task(t_task.xrun_xconsume())

        await asyncio.gather(p_task, c_task)

    asyncio.run(main())

    # ------------------------------------------------------------------------ #
    #                                  limiter                                 #
    # ------------------------------------------------------------------------ #
    # import asyncio

    # limit = Limiter('g_mkt')._set(5,1,'outflow')

    # t_task = Task('worker')
    # t_task.set_timer('every_seconds',10,'KST')
    
    # async def pub():
    #     for i in range(10):
    #         await t_task.xput_channel(args=(i/10,),msg=False)

    # t_task.set_producer(pub)

    # async def sub(sec):
    #     await asyncio.sleep(sec)

    # sub_lim = limit.wrapper(sub)

    # t_task.set_consumer(sub_lim)

    # async def main():
    #     p_task = asyncio.create_task(t_task.xrun_xproduce())
    #     c_task = asyncio.create_task(t_task.xrun_xconsume())

    #     await asyncio.gather(p_task, c_task)

    # asyncio.run(main())