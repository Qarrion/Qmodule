import asyncio
from typing import Callable

from Qtask.tools.taskq import TaskQue
from Qtask.utils.logger_custom import CustomLog

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
        self._custom.info.msg('Consume',name)

        self._consumer ={}  # consume queue in taskqueue

        self.taskque = None


    # ------------------------------------------------------------------------ #
    #                                  TaskQue                                 #
    # ------------------------------------------------------------------------ #

    # def set_taskque(self, name:str):
    #     self._custom.info.msg('tools',name)
    #     self.taskque = TaskQue(name)

    def set_taskque(self, taskque:TaskQue):
        self._custom.info.msg('tools',taskque._name)
        self.taskque = taskque

    async def xput_taskque(self, fname:str, args:tuple=(), kwargs:dict=None,
                      timeout:int=None, retry:int=0, msg=True):
        """>>> # wrapper (taskq.xput_queue)"""
        await self.taskque.xput_queue(fname, args, kwargs, timeout, retry, msg=False)
        text = f"f='{fname}' a={args}, k={kwargs} t={timeout} r={retry}"
        if msg: self._custom.info.msg('xput',text, frame = self.taskque._frame)

    async def xget_taskque(self, msg=False):
        """>>> # wrapper (taskq.xget_queue)"""
        fname, args, kwargs, timeout, retry  = await self.taskque.xget_queue(msg=False)
        if msg : self._custom.info.msg('xget',fname, f"{args}",frame=self.taskque._frame)
        return (fname, args, kwargs, timeout, retry)

    async def xrun_taskque(self, tasks:dict, item:tuple, msg=False):
        """>>> # wrapper (taskq.xrun_queue)
        # tasks: consumer """
        fname, args, kwargs, timeout, retry = item
        if kwargs is None : kwargs = {}
        if not tasks:
            print(f"\033[31m [Warning in 'xrun_taskque()'] tasks has not been set! \033[0m")
        try:
            if msg : self._custom.info.msg('xrun', fname, f"{args}",frame=self.taskque._frame)
            await asyncio.wait_for(tasks[fname](*args, **kwargs), timeout=timeout)

        except Exception as e:
            self._custom.warning.msg('except', fname, f"{args}", e.__class__.__name__,frame=self.taskque._frame)
            # print(str(e))
            # traceback.print_exc()

            if retry < 3:
                await self.xput_taskque(fname, args, kwargs, timeout, retry+1, msg=False)
                self._custom.warning.msg('retry',fname, f"{args}", f"retry({retry+1})", frame=self.taskque._frame)
            else:
                self._custom.error.msg('fail',fname, f"{args}", f"retry({retry})", frame=self.taskque._frame)
        finally:
            self.taskque.task_done()
    # ------------------------------------------------------------------------ #
    #                                  Consume                                 #
    # ------------------------------------------------------------------------ #

    def set_consumer(self, async_def: Callable, fname: str = None):
        if fname is None : fname = async_def.__name__ 
        self._consumer[fname] = async_def
        self._custom.info.msg('xdef', fname)

    async def xconsume(self, msg=True):
        while True:
            item = await self.xget_taskque(msg=msg)
            task = asyncio.create_task(self.xrun_taskque(self._consumer, item, msg=msg))
            
    # ------------------------------------------------------------------------ #
    #                                  dev_msg                                 #
    # ------------------------------------------------------------------------ #
    def _msg_consume(self, async_def, msg=True):
        if self.taskque.is_task_start():
            if msg : self._custom.info.msg()
            self._custom.info.msg('task', self._custom.arg(async_def.__name__,3,'l',"-"), frame='consume')
        elif self.taskque.is_tasks_finish():
            if msg : self._custom.info.msg()
            self._custom.info.msg('task', self._custom.arg(async_def.__name__,3,'r',"-"), frame='consume')

if __name__ == "__main__":
    taskq = TaskQue('taskq')
    cons = Consume()
    cons.set_taskque(taskq)
    # ------------------------------- producer ------------------------------- #
    async def producer():
        await cons.xput_taskque(fname='consumer',args =(1,),timeout=2)
        
    # ------------------------------- consumer ------------------------------- #
    async def consumer(var):
        print('start')
        await asyncio.sleep(3)
        print('finish')

    cons.set_consumer(consumer)

    async def main():
        task_produce = asyncio.create_task(producer())
        task_consume = asyncio.create_task(cons.xconsume())

        await asyncio.gather(task_produce,task_consume)

    asyncio.run(main())