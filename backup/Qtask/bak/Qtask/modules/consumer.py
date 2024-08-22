# -------------------------------- ver 240526 -------------------------------- #
# interrupt

import asyncio
from functools import partial
from re import M
import traceback
from typing import Callable

from Qtask.utils.logger_custom import CustomLog
from Qtask.modules.channel import Channel




class Consumer:
    """>>> # consume
    ch01 = Channel()
    cons = Consume()
    >>> # ------------------------------- producer ------------------------------- #
    async def producer():
        await cons.xput_channel(args =(1,))
        await cons.xput_channel(args =(1,))
        
    >>> # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        print('start')
        await asyncio.sleep(3)
        print('finish')
    cons.set_consumer(consumer,ch01,msg_put=True,msg_get=True,msg_run=True)

    >>> # --------------------------------- main --------------------------------- #
    async def main():
        task_produce = asyncio.create_task(producer())
        task_consume = asyncio.create_task(cons.xconsume(msg=True))
        await asyncio.gather(task_produce,task_consume)
    asyncio.run(main())
    """    
    def __init__(self, name:str='cons',msg=True):
        CLSNAME = 'Consumer'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        self._channel:Channel = None
        self._xworker = None

    # ------------------------------------------------------------------------ #
    #                                  Consume                                 #
    # ------------------------------------------------------------------------ #
    def set_channel(self, channel:Channel):
        self._channel:Channel = channel
        self._custom.info.msg(channel._name,"","")
        
    def set_xworker(self, xdef: Callable, channel:Channel=None, 
                                            msg_get=False, msg_put=False, msg_run=False):
        """arg 'channel' object should be assigned in the 'set_producer' or 'set_channel'
        + msg for | xget_queue....item | """

        self._custom.info.msg(xdef.__name__,"","")
        self._xworker = xdef
        self._msg_channel_get = msg_get
        self._msg_channel_put = msg_put
        self._msg_channel_run = msg_run

        if channel is not None:
            self.set_channel(channel)

    def set_partial(self, func, *args, **kwargs):
        punc = partial(func, *args, **kwargs)
        punc.__name__ = func.__name__
        return punc

    async def xput_channel(self, args: tuple=(), kwargs: dict = None, retry: int = 0):
        """
        + args = () for no arg consumer
        + msg in set_xworker"""
        await self._channel.xput_queue(args,kwargs,retry,msg=self._msg_channel_put)

    # -------------------------- run_without_context ------------------------- #
    async def xget_channel(self):
        """+ msg in set_xworker"""
        return await self._channel.xget_queue(msg=self._msg_channel_get)
    
    async def xrun_channel(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg_div=False):
        if self._channel.is_starting():
            if msg_div : self._custom.info.msg(xdef.__name__,widths=(3,),aligns=("<"),paddings=("-"))

        await self._channel.xrun_queue(xdef, item, timeout, maxtry,msg=self._msg_channel_run)

        if self._channel.is_stopping():
            if msg_div : self._custom.info.msg(xdef.__name__,widths=(3,),aligns=(">"),paddings=("-"))

    async def xconsume(self, timeout:int=None, maxtry:int=3, msg_div=False):
        if not self._xworker:  
            print(f"\033[31m [Warning in 'xconsume()'] 'xworker' has not been set! \033[0m")
            return

        while True:
            try:
                item = await self.xget_channel()
                task = asyncio.create_task(self.xrun_channel(self._xworker,item,timeout,maxtry,msg_div=msg_div))
            except asyncio.exceptions.CancelledError:
                print(f"\033[33m Interrupted ! loop_xconsume ({self._xworker.__name__}) \033[0m")
                break      
            except Exception as e:
                print(e.__class__.__name__)      
                traceback.print_exc()


if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                  consume                                 #
    # ------------------------------------------------------------------------ #
    cons = Consumer()
    # ------------------------------- producer ------------------------------- #
    async def producer():
        await cons.xput_channel(args =(1,))
        # await cons.xput_channel(args =(1,))
    
    # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        print('start')
        raise ValueError
        await asyncio.sleep(3)
        print('finish')

    # #! channel
    ch01 = Channel(msg=False)
    cons.set_xworker(consumer,ch01,msg_get=True, msg_put=True, msg_run=True)

    # # async def main():
    # #     task_produce = asyncio.create_task(producer())
    # #     task_consume = asyncio.create_task(cons.xconsume(msg=True))

    # #     await asyncio.gather(task_produce,task_consume)

    async def main():
        tasks =[
        asyncio.create_task(producer()),
        asyncio.create_task(cons.xconsume(msg_div=True)),
        ]    

        await asyncio.gather(*tasks)

    asyncio.run(main())