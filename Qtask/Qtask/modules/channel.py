# -------------------------------- ver 240714 -------------------------------- #
# args is None / xrun_queue

from typing import Callable
from Qtask.utils.logger_custom import CustomLog
import asyncio
import traceback





class Channel:
    """
    >>> # channel
    channel = Channel()

    >>> # ------------------------------- consumer ------------------------------- #
    async def xrun(x,y,z):
        await asyncio.sleep(2)
        print(x,y,z)

    >>> # --------------------------------- basic -------------------------------- #
    async def main():
        await channel.xput_queue((1,2,3), msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,msg=True)
    asyncio.run(main())
    """
    def __init__(self, name:str='channel',msg=True):
        CLSNAME = 'Channel'
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._name = name
        self._custom = CustomLog(logger,CLSNAME,'async')

        if msg: self._custom.info.ini(name)
        self._lock = asyncio.Lock()
        self._queue = asyncio.Queue()
        self._status = 'stop'
        
    async def xput_queue(self, 
        args:tuple=(),kwargs:dict=None, retry:int=0, msg=False):
        """args = () for no arg consumer"""
        item = (args,kwargs,retry)
        await self._queue.put(item)
        if msg: self._custom.info.msg(str(args),f'retry({retry})','')

    async def xget_queue(self,msg=False):
        """return (args, kwargs, retry) """
        args, kwargs, retry = await self._queue.get()
        if msg: self._custom.info.msg(str(args),f'retry({retry})','')
        return (args, kwargs, retry)

    async def xget_queue_with_timeout(self, timeout:int, msg=False):
        args, kwargs, retry = await asyncio.wait_for(self._queue.get(), timeout=timeout)
        if msg: self._custom.info.msg(str(args),f'retry({retry})','')
        return (args, kwargs, retry)
        
    async def xrun_queue(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg=False):
        args, kwargs, retry = item

        try:
            if msg: self._custom.info.msg(str(args),f'retry({retry})','')
            if args is None : args = ()
            if kwargs is None : 
                await asyncio.wait_for(xdef(*args), timeout=timeout)
            else:
                await asyncio.wait_for(xdef(*args, **kwargs), timeout=timeout)

        except Exception as e:
            if retry < maxtry:
                self._custom.warning.msg('except',e.__class__.__name__)
                await self.xput_queue(args, kwargs,retry+1,msg=True)
                # traceback.print_exc()
            else:
                self._custom.error.msg('failed',e.__class__.__name__)
                traceback.print_exc()
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
    async def main():
        await channel.xput_queue((1,2,3), msg=True)
        item = await channel.xget_queue(msg=True)
        await channel.xrun_queue(xrun,item,msg=True)

    asyncio.run(main())

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
    