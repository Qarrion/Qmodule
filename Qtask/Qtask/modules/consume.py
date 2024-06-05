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
    def __init__(self, name:str='consume',msg=True):
        CLSNAME = 'Consume'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.msg(name)

        self._channel:Channel = None
        self._consumer = None

        self._is_msg_channel_get = False
        self._is_msg_channel_put = False
        self._is_msg_channel_run = False

    # ------------------------------------------------------------------------ #
    #                                  Consume                                 #
    # ------------------------------------------------------------------------ #
    def set_channel(self, channel:Channel):
        self._channel = channel
        
    def set_xconsumer(self, xdef: Callable, channel:Channel=None, 
                                            msg_get=False, msg_put=False, msg_run=False):
        """arg 'channel' object should be assigned in the 'set_producer' or 'set_channel'
        + msg for | xget_queue....item | """
        self._is_msg_channel_get = msg_get
        self._is_msg_channel_put = msg_put
        self._is_msg_channel_run = msg_run
        self._consumer = xdef
        if channel is None:
            self._custom.info.msg('xdef', xdef.__name__, 'None')
        else:
            self._channel:Channel = channel
            self._custom.info.msg('xdef', xdef.__name__, channel._name)

    async def xput_channel(self, args: tuple=(), kwargs: dict = None, retry: int = 0):
        """
        + args = () for no arg consumer
        + msg in set_xproducer"""
        msg_put = self._is_msg_channel_put
        if self._channel is None:  
            print(f"\033[31m [Warning in 'xput_channel()'] 'channel' has not been set! \033[0m")
        await self._channel.xput_queue(args,kwargs,retry, msg_put)


    # -------------------------- run_without_context ------------------------- #
    async def xget_channel(self):
        """+ msg in set_xproducer"""
        msg_get = self._is_msg_channel_get
        item = await self._channel.xget_queue(msg_get)
        return item
    
    async def xrun_channel(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg=False):
        msg_run = self._is_msg_channel_run
        self._msg_consume(xdef, msg=msg)
        await self._channel.xrun_queue(xdef,item,timeout,maxtry,msg_run)
        self._msg_consume(xdef, msg=msg)

    async def xconsume(self, timeout:int=None, maxtry:int=3, msg=False):
        assert self._consumer is not None, "no _consumer"

        while True:
            try:
                item = await self.xget_channel()
                task = asyncio.create_task(
                    self.xrun_channel(self._consumer,item,timeout,maxtry,msg=msg))
            except asyncio.exceptions.CancelledError:
                print(f"\033[33m Interrupted ! loop_xconsume ({self._consumer.__name__}) \033[0m")
                break      
            except Exception as e:
                print(e.__class__.__name__)      
                # break      

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

    cons.set_xconsumer(consumer,ch01,msg_put=True,msg_get=True,msg_run=True)

    # async def main():
    #     task_produce = asyncio.create_task(producer())
    #     task_consume = asyncio.create_task(cons.xconsume(msg=True))

    #     await asyncio.gather(task_produce,task_consume)

    async def main():
        task_consume = asyncio.create_task(cons.xconsume_with_xsess(msg=True))

        await asyncio.gather(task_consume)

    asyncio.run(main())