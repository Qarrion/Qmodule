import asyncio
from typing import Literal, Callable

from Qconsume.tools.taskq import Taskq

from Qconsume.utils.logger_custom import CustomLog


#TODO docstring -> example -> aeqzro
class Consume:
    """
    >>> #basic
    cons = Consume()
    taskq = cons.taskq

    >>> #produce
    async def produce():
        taskq.xenqueue(fname='consumer', args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=True)
    
    >>> #consume
    async def consume():
        await asyncio.create_task(cons.cumsume())
    """
    def __init__(self, name:str='consume'):

        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None

        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Consume')

        self._taskq = Taskq(logger) 

        self._tasks = {}

    def set_task(self, async_def: Callable, fname: str = None):
        if fname is None : fname = async_def.__name__ 
        self._tasks[fname] = async_def
        self._custom.info.msg('xdef', fname)

    def share_taskq(self):
        """ >>> # in producer task : 
        taskq.xenqueue(fname, args, kwargs, timeout, retry)"""
        return self._taskq

    @property
    def taskq(self):
        return self._taskq
    
    async def xenqueue(self, fname:str, args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=True):
        
        await self._taskq.xenqueue(fname=fname, args=args, kwargs=kwargs,
                            timeout=timeout,retry=retry, msg=msg)
        
    async def consume(self,msg=True):
        while True:
            item = await self._taskq.xdequeue()
            task = asyncio.create_task(self._taskq.xexecute(self._tasks, item,msg=msg))
            
    # ------------------------------------------------------------------------ #
    #                                  dev_msg                                 #
    # ------------------------------------------------------------------------ #
    def _msg_consume(self):
        if self._taskq.is_task_start():
            if msg : self._custom.info.msg()
        elif self._taskq.is_tasks_finish():
            if msg : self._custom.info.msg()
            self._custom.info.msg('task', self._custom.arg(async_def.__name__,3,'r',"-"), frame='produce', offset=Core.offset)

if __name__ == "__main__":
    cons = Consume()

    # ------------------------------- producer ------------------------------- #
    taskq = cons.taskq
    async def producer():
        await taskq.xenqueue(fname='consumer',args =(1,))

        
    # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        await asyncio.sleep(var)

    cons.set_task(consumer)

    async def main():
        task_produce = asyncio.create_task(producer())
        task_consume = asyncio.create_task(cons.consume())

        await asyncio.gather(task_produce,task_consume)


    asyncio.run(main())