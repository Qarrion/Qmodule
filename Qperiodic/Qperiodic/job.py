from Qperiodic.utils.log_custom import CustomLog
from typing import Coroutine
import asyncio
import logging





class Job:


    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'async')
        self.registry = dict()
        self.queue = asyncio.Queue()

    def register(self, coro:Coroutine, fname:str=None):
        if fname is None : fname = coro.__name__ 
        self.registry[fname] = coro
        self.custom.info.msg('done', fname,task=True)

    async def enqueue(self, 
                      fname:str, args:tuple=(), kwargs:dict=None, timeout:int=None, retry:int=0,
                      msg=True):
        """enqueue fname, args, kwargs"""
        item = (fname, args, kwargs, timeout, retry)
    
        await self.queue.put(item)
        if msg: self.custom.debug.msg('done', fname, f"{args}",task=True)

    async def dequeue(self):
        fname, args, kwargs, timeout, retry = await self.queue.get()
        self.custom.debug.msg('done',fname, f"{args}", f"retry({retry})", task=True)
        return (fname, args, kwargs, timeout, retry)
    
    async def execute(self, item):
        fname, args, kwargs, timeout, retry = item
        if kwargs is None : kwargs = {}

        try:
            result = await asyncio.wait_for(self.registry[fname](*args, **kwargs), timeout=timeout)
            self.custom.info.msg('done',fname, f"{args}",task=True)
            
        except Exception as e:

            self.custom.warning.msg('except', fname, e.__class__.__name__,task=True)
            if retry <3:
                await self.enqueue(fname, args, kwargs, timeout, retry+1, msg=False)
                self.custom.warning.msg('retry',fname, f"{args}", task=True)
            else:
                self.custom.error.msg('fail',fname, f"{args}", task=True)


if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test','head')

    job = Job(logger)

    import random
    async def main():

        async def work(item):
            # item = random.randint(1, 5) 
            print(f'work {item} start')
            await asyncio.sleep(item)
            print(f'work {item} finish')

        async def err(item):
            # item = random.randint(1, 5) 
            print(f'err {item} start')
            raise Exception('err occur')
            print(f'err {item} finish')


        job.register(work)
        job.register(err)

        item = random.randint(1, 5) 
        await job.enqueue('work',args=(item,),timeout=10)
        item = await job.dequeue()
        await job.execute(item)

        item = random.randint(1, 5) 
        await job.enqueue('err',args=(item,),timeout=10)
        item = await job.dequeue()
        await job.execute(item)
        item = await job.dequeue()
        await job.execute(item)
        item = await job.dequeue()
        await job.execute(item)
        item = await job.dequeue()
        await job.execute(item)
        item = await job.dequeue()
        await job.execute(item)

    asyncio.run(main())