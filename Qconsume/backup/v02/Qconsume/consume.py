import asyncio
import logging
from typing import Literal, Callable

from Qconsume.tools.taskq import Taskq
from Qconsume.tools.limit import Limit
import time

from Qconsume.utils.logger_custom import CustomLog



class Consume:
    """
    >>> #basic
    cons = Consume(logger)
    cons.set_limiter(5,1,'outflow')

    """
    def __init__(self, logger: logging.Logger = None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Consume')

        self._taskq = Taskq(logger)
        self._limit = Limit(logger)

        self._tasks = {}

    def set_limiter(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow']):
        self._is_limiter = True
        self._limit.set_rate(max_worker=max_worker, seconds=seconds,limit=limit)

    def set_task(self, async_def: Callable, fname: str = None):
        self._warning_default_core('consumer.register()')
        if fname is None : fname = async_def.__name__ 
        self._tasks[fname] = self._limit._wrapper_throttle(async_def)
        self._custom.info.msg('', fname, task=False)

    def _warning_default_core(self, where):
        if not hasattr(self, '_is_limiter'):
            print(f"\033[31m [Warning in '{where}'] limiter has not been set! \033[0m")

    def get_taskq(self):
        return self._taskq

    @property
    def taskq(self):
        return self._taskq
    
    def enqueue(self, fname:str, args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=True):
        self._taskq.xenqueue(fname=fname, args=args, kwargs=kwargs,
                            timeout=timeout,retry=retry, msg=msg)
    async def consume(self):
        while True:
            item = await self._taskq.xdequeue()
            # await self._taskq.xexecute(self._tasks, item)
            task = asyncio.create_task(self._taskq.xexecute(self._tasks, item))
            
    # ------------------------------------------------------------------------ #
    #                                  dev_msg                                 #
    # ------------------------------------------------------------------------ #


if __name__ == "__main__":
    from Qconsume .utils .logger_color import ColorLog

    logger = ColorLog('cons','blue')
    
    cons = Consume(logger)
    cons.set_limiter(5, 1, 'inflow')

    log_func = ColorLog('work', 'yellow')
    async def myfun(a,b,c):
        log_func.info('start')
        await asyncio.sleep(0.4)
        log_func.info('end')

    cons.set_task(myfun)

    async def put():
        taskq = cons.get_taskq()
        await taskq.xenqueue('myfun',(1,0,0))
        await asyncio.sleep(0.1)
        await taskq.xenqueue('myfun',(2,0,0))
        await asyncio.sleep(0.1)
        await taskq.xenqueue('myfun',(3,0,0))
        await asyncio.sleep(0.1)
        # await taskq.xenqueue('myfun',(4,0,0))
        # await taskq.xenqueue('myfun',(5,0,0))
        # await taskq.xenqueue('myfun',(6,0,0))
        # await taskq.xenqueue('myfun',(7,0,0))

    # async def run():
    #     item = await cons.dequeue()
    #     await cons.execute(item)

    async def main():
        # await put()
        # await cons.consume()
        task_putlike = asyncio.create_task(put())
        task_consume = asyncio.create_task(cons.consume())

        await asyncio.gather(task_putlike, task_consume)

    asyncio.run(main())
    