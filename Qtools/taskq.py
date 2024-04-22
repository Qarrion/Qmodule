from Qutils.logger_custom import CustomLog

from typing import Coroutine, Callable
import asyncio, logging





class Taskq:

    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'async')
        self.custom.info.msg('Taskq')

        self.registry = dict()
        self.queue = asyncio.Queue()

    # ------------------------------------------------------------------------ #
    #                               register task                              #
    # ------------------------------------------------------------------------ #
    def register(self, async_def:Callable, fname:str=None):
        if fname is None : fname = async_def.__name__ 
        self.registry[fname] = async_def
        self.custom.info.msg('async_def', fname, task=False)

    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #
    async def enqueue(self, fname:str, args:tuple=(), kwargs:dict=None, 
                      timeout:int=None, retry:int=0, msg=True):
        """enqueue fname, args, kwargs"""
        item = (fname, args, kwargs, timeout, retry)
    
        await self.queue.put(item)
        if msg: self.custom.debug.msg('put', fname, f"{args}",task=True)
    # ------------------------------------------------------------------------ #
    async def dequeue(self, msg=True):
        fname, args, kwargs, timeout, retry = await self.queue.get()
        if msg : self.custom.debug.msg('get',fname, f"{args}", task=True)
        return (fname, args, kwargs, timeout, retry)

    async def execute(self, item):
        """with timeout"""
        fname, args, kwargs, timeout, retry = item
        if kwargs is None : kwargs = {}

        try:
            result = await asyncio.wait_for(self.registry[fname](*args, **kwargs), timeout=timeout)
            self.custom.info.msg('done',fname, f"{args}",task=True)
            
        except Exception as e:
            self.custom.warning.msg('except', fname, e.__class__.__name__,str(e),task=True)
            if retry < 3:
                await self.enqueue(fname, args, kwargs, timeout, retry+1, msg=False)
                self.custom.warning.msg('retry',fname, f"{args}", f"retry({retry})", task=True)
            else:
                self.custom.error.msg('fail',fname, f"{args}", f"retry({retry})", task=True)
        finally:
            self.queue.task_done()

        if self.queue._unfinished_tasks == 0:
            self.custom.info.msg('all done', "_unfinished_tasks = 0")

if __name__ == "__main__":
    from Qutils.logger_color import ColorLog

    async def myfun(a,b,c):
        print('s')
        await asyncio.sleep(3)
        print(a,b,c)
        print('e')

    async def main():
        
        logger = ColorLog('test','green')
        taskq = Taskq(logger)
        taskq.register(myfun)
        print(taskq.registry)

        # ------------------------------- done ------------------------------- #
        # await taskq.enqueue('myfun', (1,2),{'c':3},timeout=5)
        # item = await taskq.dequeue()
        # await taskq.execute(item)

        # ------------------------------- retry ------------------------------ #
        await taskq.enqueue('myfun', (1,2),{'c':3},timeout=2)
        item = await taskq.dequeue()
        await taskq.execute(item)
        item = await taskq.dequeue()
        await taskq.execute(item)
        item = await taskq.dequeue()
        await taskq.execute(item)
        item = await taskq.dequeue()
        await taskq.execute(item)
        item = await taskq.dequeue()
        await taskq.execute(item)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()