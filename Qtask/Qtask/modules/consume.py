# -------------------------------- ver 240526 -------------------------------- #
# interrupt

import asyncio
from typing import Callable

from Qtask.utils.logger_custom import CustomLog
from Qtask.modules.channel import Channel




class Consume:
    """>>> # consume
    ch01 = Channel()
    cons = Consume()
    cons._debug_queue = True
    >>> # ------------------------------- producer ------------------------------- #
    async def producer():
        await cons.xput_channel(args =(1,))
        await cons.xput_channel(args =(1,))
        
    >>> # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        print('start')
        await asyncio.sleep(3)
        print('finish')
    cons.set_consumer(consumer,ch01)

    >>> # --------------------------------- main --------------------------------- #
    async def main():
        task_produce = asyncio.create_task(producer())
        task_consume = asyncio.create_task(cons.xconsume())
        await asyncio.gather(task_produce,task_consume)
    asyncio.run(main())
    """    
    def __init__(self, name:str='consume',msg=True):
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,'async')
        if msg : self._custom.info.msg('Consume',name)

        self._channel:Channel = None
        self._consumer = None

        self._debug_queue = False
    # ------------------------------------------------------------------------ #
    #                                  Consume                                 #
    # ------------------------------------------------------------------------ #
    def set_channel(self, channel:Channel):
        self._channel = channel
        
    def set_consumer(self, xdef: Callable, channel:Channel=None):
        """arg 'channel' object should be assigned in the 'set_producer' or 'set_channel'"""
        self._consumer = xdef
        if channel is None:
            self._custom.info.msg('xdef', xdef.__name__, 'None')
        else:
            self._channel:Channel = channel
            self._custom.info.msg('xdef', xdef.__name__, channel._name)

    async def xput_channel(self, args: tuple=(), kwargs: dict = None, retry: int = 0, msg: bool = False):
        """args = () for no arg consumer"""
        is_msg = True if msg else self._debug_queue

        if self._channel is None:  
            print(f"\033[31m [Warning in 'xput_channel()'] 'channel' has not been set! \033[0m")
        await self._channel.xput_queue(args,kwargs,retry, is_msg)

    async def xget_channel(self, msg=False):
        is_msg = True if msg else self._debug_queue
        item = await self._channel.xget_queue(is_msg)
        return item

    async def xrun_channel(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg=False):
        is_msg = True if msg else self._debug_queue
        self._msg_consume(xdef,msg=True)
        await self._channel.xrun_queue(xdef,item,timeout,maxtry,is_msg)
        self._msg_consume(xdef,msg=True)

    async def xconsume(self, timeout:int=None, maxtry:int=3, msg=False):
        is_msg = self._debug_queue
        while True:
            try:
                item = await self.xget_channel(msg=is_msg)
                task = asyncio.create_task(
                    self.xrun_channel(self._consumer,item,timeout,maxtry,msg=msg))
            except asyncio.exceptions.CancelledError:
                print(f"\033[33m Interrupted ! loop_xconsume ({self._consumer.__name__}) \033[0m")
                break      
            except Exception as e:
                print(e.__class__.__name__)      
                break      
    # ------------------------------------------------------------------------ #
    #                                  dev_msg                                 #
    # ------------------------------------------------------------------------ #
    def _msg_consume(self, xdef, msg=True):
        if self._channel.is_starting():
            if msg : self._custom.info.msg('task', self._custom.arg(xdef.__name__,3,'l',"-"), frame='xconsume')
        elif self._channel.is_stopping():
            if msg : self._custom.info.msg('task', self._custom.arg(xdef.__name__,3,'r',"-"), frame='xconsume')

if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                  consume                                 #
    # ------------------------------------------------------------------------ #
    cons = Consume()
    cons._debug_queue = True
    # ------------------------------- producer ------------------------------- #
    async def producer():
        await cons.xput_channel(args =(1,))
        await cons.xput_channel(args =(1,))
    
    # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        print('start')
        await asyncio.sleep(3)
        print('finish')

    #! channel
    ch01 = Channel()

    cons.set_consumer(consumer,ch01)

    async def main():
        task_produce = asyncio.create_task(producer())
        task_consume = asyncio.create_task(cons.xconsume())

        await asyncio.gather(task_produce,task_consume)

    asyncio.run(main())