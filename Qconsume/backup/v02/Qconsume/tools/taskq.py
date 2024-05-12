import time
from Qconsume.utils.logger_custom import CustomLog

from typing import Callable
import asyncio, logging, traceback





class Taskq:

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')
        self._queue = asyncio.Queue()

    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    # -------------------------------- enqueue ------------------------------- #
    async def xenqueue(self, fname:str, args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=True):
        """enqueue fname, args, kwargs"""
        item = (fname, args, kwargs, timeout, retry)
        await self._queue.put(item)
        if msg: self._custom.debug.msg('put', fname, f"{args}",task=True)

    # -------------------------------- dequeue ------------------------------- #
    async def xdequeue(self, msg=True):
        fname, args, kwargs, timeout, retry = await self._queue.get()
        if msg : self._custom.debug.msg('get',fname, f"{args}", task=True)
        return (fname, args, kwargs, timeout, retry)

    # -------------------------------- execute ------------------------------- #
    async def xexecute(self, tasks:dict, item:tuple):
        """with timeout"""
        fname, args, kwargs, timeout, retry = item
        if kwargs is None : kwargs = {}
        #! TODO if timeout is None
        try:
            await asyncio.wait_for(tasks[fname](*args, **kwargs), timeout=timeout)
            self._custom.info.msg('done',fname, f"{args}",task=True)
            
        except Exception as e:
            self._custom.warning.msg('except', fname, e.__class__.__name__,task=True)
            # print(str(e))
            traceback.print_exc()

            if retry < 3:
                await self.xenqueue(fname, args, kwargs, timeout, retry+1, msg=False)
                self._custom.warning.msg('retry',fname, f"{args}", f"retry({retry})", task=True)
            else:
                self._custom.error.msg('fail',fname, f"{args}", f"retry({retry})", task=True)
        finally:
            self._queue.task_done()

        if self._queue._unfinished_tasks == 0:
            self._custom.info.msg('all done', "_unfinished_tasks = 0")

if __name__ == "__main__":
    from Qconsume.utils.logger_color import ColorLog
    log_func = ColorLog('work', 'yellow')

    async def myfun(a,b,c):
        log_func.info('start')
        await asyncio.sleep(3)
        log_func.info('end')

    async def main():
        
        logger = ColorLog('test','green')
        taskq = Taskq(logger)
        taskq.register(myfun)

        # ------------------------------- done ------------------------------- #
        await taskq.xenqueue('myfun', (1,2),{'c':3},timeout=5)
        item = await taskq.xdequeue()
        await taskq.xexecute(item)

        # ------------------------------- retry ------------------------------ #
        # await taskq.enqueue('myfun', (1,2),{'c':3},timeout=2)
        # item = await taskq.dequeue()
        # await taskq.execute(item)
        # item = await taskq.dequeue()
        # await taskq.execute(item)
        # item = await taskq.dequeue()
        # await taskq.execute(item)
        # item = await taskq.dequeue()
        # await taskq.execute(item)
        # item = await taskq.dequeue()
        # await taskq.execute(item)

    asyncio.run(main())

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()