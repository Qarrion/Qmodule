# -------------------------------- ver 240521 -------------------------------- #
# set_channel
# -------------------------------- ver 240714 -------------------------------- #
# set_offset in consumer
# ---------------------------------------------------------------------------- #

import traceback
from typing import Callable, Literal

from Qtask.modules.producer import Producer
from Qtask.modules.consumer import Consumer
from Qtask.modules.channel import Channel
from Qtask.utils.logger_custom import CustomLog
import asyncio

class Task:
    def __init__(self,name:str='task',msg=True):
        CLSNAME = 'Task'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.ini(name)
        
        self.channel = Channel(name,msg=False)
        self.consume = Consumer(name,custom=self._custom, msg=False)
        self.produce = Producer(name,custom=self._custom, msg=False)

        self.consume.set_offset(self.produce.core)
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

    def set_xproducer(self,xdef:Callable=None, args:tuple=None, kwargs:dict=None, msg=False):
        """+ produce
        + if xdef is none then default without arguments producer with args, kwargs
        + msg for | xput_queue....item |
        >>>  # producer
        xput_channel(args=(),kwargs=None,retry=0)
        """

        if xdef is None:
            async def xproducer():
                await self.xput_channel(args=args, kwargs=kwargs)

            self.produce.set_xworker(xdef=xproducer, channel=None, msg=msg)
        else:
            self.produce.set_xworker(xdef=xdef, channel=None, msg=msg)

    async def xput_channel(self,args:tuple=(), kwargs:dict=None, retry= 0,msg=False):
        """ 
        + in xproduce custom xdef -> set_producer(xdef)
        + args = () for no arg consumer"""
        await self.produce.xput_channel(args,kwargs,retry,msg=msg)

    async def xrun_xproduce(self,timeout=50,msg=True):
        await self.produce.xproduce(timeout=timeout,msg_div=msg)

    # ------------------------------------------------------------------------ #
    #                                   cons                                   #
    # ------------------------------------------------------------------------ #
    def set_xconsumer(self,xdef:Callable,msg_get = False, msg_put = False, msg_run = False):
        self.consume.set_xworker(xdef=xdef, channel=None,
                                   msg_get=msg_get,msg_put=msg_put,msg_run=msg_run)

    async def xrun_xconsume(self,timeout:int=None, maxtry:int=3, msg=False):
        await self.consume.xconsume(timeout=timeout, maxtry=maxtry, msg_div=msg)

    async def xrun(self,timeout:int=None, maxtry:int=3, msg=True):
        task_prod = asyncio.create_task(self.produce.xproduce(timeout=timeout,msg_div=msg))
        task_cons = asyncio.create_task(self.consume.xconsume(timeout=timeout, maxtry=maxtry, msg_div=msg))
        await asyncio.gather(task_prod,task_cons)

    def task_done(self):
        self.channel._queue.task_done()

    def get_unfinished_task(self):
        return self.channel._queue._unfinished_tasks

if __name__ == "__main__":

    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    import asyncio

    t_task = Task('worker')
    t_task.set_timer('every_seconds',10,'KST')
    
    # async def pub():
    #     for i in range(10):
    #         # await t_task.xput_channel(args=(i/10,))
    #         await t_task.xput_channel(kwargs=dict(sec=i/10))

    # t_task.set_xproducer(pub)

    t_task.set_xproducer(kwargs={'sec':1})
    # t_task.set_xproducer(args=(1,))

    async def sub(sec):
        print(f"sub {sec} start")
        await asyncio.sleep(sec)
        print(f"sub {sec} finish")

    t_task.set_xconsumer(sub)

    async def main():
        p_task = asyncio.create_task(t_task.xrun_xproduce())
        c_task = asyncio.create_task(t_task.xrun_xconsume())

        await asyncio.gather(p_task, c_task)

    asyncio.run(main())

 