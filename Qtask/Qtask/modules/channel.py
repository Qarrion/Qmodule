from typing import Callable
from Qtask.utils.logger_custom import CustomLog
import asyncio, logging






class Channel:

    def __init__(self, name:str='channel',msg=True):
        
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._name = name
        self._custom = CustomLog(logger,'async')

        if msg: self._custom.info.msg('Channel',name)
        self._queue = asyncio.Queue()
        self._status = 'stop'

    def _msg_args(self, status, args, kwargs, retry):
        if kwargs is None:
            text= f"retry({retry}), {args}"    
        else:
            text= f"retry({retry}), {args + tuple(kwargs.values())}"
        self._custom.info.msg(status, text,frame=2)
        
    async def xput_queue(self, 
        args:tuple=(),kwargs:dict=None, retry:int=0, msg=False):
        """args = () for no arg consumer"""
        item = (args,kwargs,retry)
        await self._queue.put(item)
        if msg: self._msg_args('item',args, kwargs, retry)

    async def xget_queue(self,msg=False):
        args, kwargs, retry = await self._queue.get()
        if msg: self._msg_args('item',args, kwargs, retry)
        return (args, kwargs, retry)

    async def xget_queue_with_timeout(self, timeout:int, msg=False):
        args, kwargs, retry = await asyncio.wait_for(self._queue.get(), timeout=timeout)
        if msg: self._msg_args('item',args, kwargs, retry)
        return (args, kwargs, retry)
        
    async def xrun_queue(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg=False):
        args, kwargs, retry = item

        try:
            if msg: self._msg_args('xdef',args, kwargs, retry)
            if kwargs is None : 
                await asyncio.wait_for(xdef(*args), timeout=timeout)
            else:
                await asyncio.wait_for(xdef(*args, **kwargs), timeout=timeout)

        except Exception as e:
            if retry < maxtry:
                self._custom.warning.msg('except',e.__class__.__name__)
                await self.xput_queue(args, kwargs,retry+1,msg=True)
            else:
                self._custom.error.msg('failed',e.__class__.__name__)
        finally:
            self.task_done()
    
    def task_done(self):
        self._queue.task_done()

    def is_starting(self):
        if self._queue._unfinished_tasks != 0 and self._status=='stop':
            self._status = 'start'
            return 1
        else:
            return 0
    def is_stopping(self):
        if self._queue._unfinished_tasks == 0 and self._status=='start':
            self._status = 'stop'
            return 1
        else:
            return 0

if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                  Channel                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- common -------------------------------- #
    channel = Channel()

    async def xrun(x,y,z):
        await asyncio.sleep(2)
        print(x,y,z)

    # --------------------------------- basic -------------------------------- #
    # async def main():
    #     await channel.xput_queue((1,2,3), msg=True)
    #     item = await channel.xget_queue(msg=True)
    #     await channel.xrun_queue(xrun,item,msg=True)

    # asyncio.run(main())

    # ------------------------------- exception ------------------------------ #
    async def main():
        await channel.xput_queue((1,2,3), msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,timeout=1,msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,timeout=1,msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,timeout=1,msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,timeout=1,msg=True)

    asyncio.run(main())
    # ------------------------------------------------------------------------ #
    