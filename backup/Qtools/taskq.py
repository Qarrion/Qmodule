import asyncio
import logging
from typing import Callable

from Qutils.logger_custom import CustomLog





class Taskq:

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')

    # def __init__(self, name:str='channel'):
        
    #     try:
    #         from Qlogger import Logger
    #         logger = Logger(name,'head')
    #     except ModuleNotFoundError as e:
    #         logger = None
    #         print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,'async')
        # self._custom.info.msg('Taskq',name)

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
        item = (args,kwargs,retry)
        await self._queue.put(item)
        if msg: self._msg_args('item',args, kwargs, retry)

    async def xget_queue(self,msg=False):
        args, kwargs, retry = await self._queue.get()
        if msg: self._msg_args('item',args, kwargs, retry)
        return (args, kwargs, retry)
        
    async def xrun_queue(self, xdef:Callable, item:tuple, timeout:int=None, maxtry=3, msg=False):
        print( self._queue._unfinished_tasks, self._status)
        self._msg_consume(xdef,msg=True)
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
                await self.xput_queue(args, kwargs,retry+1,msg)
            else:
                self._custom.error.msg('failed',e.__class__.__name__)
        finally:
            self.task_done()
        self._msg_consume(xdef,msg=True)
    
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

    def _msg_consume(self, xdef, msg=True):
        if self.is_starting():
            if msg : self._custom.info.msg('task', self._custom.arg(xdef.__name__,3,'l',"-"), frame='xconsume')
        elif self.is_stopping():
            if msg : self._custom.info.msg('task', self._custom.arg(xdef.__name__,3,'r',"-"), frame='xconsume')

if __name__ == "__main__":

    # ------------------------------------------------------------------------ #
    #                                  Channel                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- common -------------------------------- #
    taskq = Taskq()

    async def xrun(x,y,z):
        await asyncio.sleep(2)
        print(x,y,z)

    # --------------------------------- basic -------------------------------- #
    async def main():
        await taskq.xput_queue((1,2,3), msg=True)
        item = await taskq.xget_queue(msg=True)
        await taskq.xrun_queue(xrun,item,msg=True)

    asyncio.run(main())

    # ------------------------------- exception ------------------------------ #
    # async def main():
    #     await taskq.xput_queue((1,2,3), msg=True)
    #     item = await taskq.xget_queue(msg=True)
    #     await taskq.xrun_queue(xrun,item,timeout=1,msg=True)
    #     item = await taskq.xget_queue(msg=True)
    #     await taskq.xrun_queue(xrun,item,timeout=1,msg=True)
    #     item = await taskq.xget_queue(msg=True)
    #     await taskq.xrun_queue(xrun,item,timeout=1,msg=True)
    #     item = await taskq.xget_queue(msg=True)
    #     await taskq.xrun_queue(xrun,item,timeout=1,msg=True)

    # asyncio.run(main())