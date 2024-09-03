




import asyncio
from Qlogger import Logger
from Qtask.utils.custom_print import cprint
from collections import namedtuple
# Item = namedtuple('item', ['future', 'xdef', 'args', 'kwargs', 'retry'])
Item = namedtuple('item', ['xdef', 'args', 'kwargs'])
from functools import wraps

class Pooler:
    
    def __init__(self, name:str='worker', msg=False):
        self._logger = Logger(logname=name, clsname='Worker', msg=msg, context='async')
        self._name = name
        
        self._work = asyncio.Queue()
        self._fail = asyncio.Queue()
        self._event = asyncio.Event()
        self._workers = dict()
        
        self.set_config()
        
    def set_config(self, n_worker = 10, timeout=None, msg_worker=True):
        self._n_worker = n_worker
        self._s_timeout = timeout
        
        self._msg_worker = msg_worker
            
    async def _pool_worker(self):
        task_name = asyncio.current_task().get_name()
        if self._msg_worker : cprint(f" - worker ({task_name}) start",'yellow')
        while True:
            item:Item = await self._work.get()
            if item is None :break
            
            try:
                result = await asyncio.wait_for(item.xdef(*item.args, **item.kwargs), timeout=self._s_timeout)
                
            except Exception as e:
                await self._fail.put(item)
    
            finally:
                self._work.task_done()
                
        if self._msg_worker : cprint(f" - worker ({task_name}) closed",'yellow')
    
    # ----------------------------- pool_monitor ----------------------------- #
    async def _pool_monitor(self):
        while True:
            total = len(self._workers)
            done = len([t for t in self._workers if self._workers[t].done()])
            print(f'worker({done}/{total-done}/{total}) done({self._work.qsize()}) fail({self._fail.qsize()})')
            await asyncio.sleep(1)
            
    def pool_monitor(self):
        task =  asyncio.create_task(self._pool_monitor(), name=f'{self._name}-monitor')
        return task 
            
    # ------------------------------ pool_start ------------------------------ #
    def pool_start(self):
        task =  asyncio.create_task(self._pool_start(), name=f'{self._name}-pool')
        return task 
    
    async def _pool_start(self):
        task_name = asyncio.current_task().get_name()
        try:
            if self._msg_worker : cprint(f" + pool ({task_name}) start",'yellow')
            while True:
                async with asyncio.TaskGroup() as tg:
                    for i in range(self._n_worker):
                        task = tg.create_task(self._pool_worker(),name=f"{self._name}-{i}")
                        self._workers[f"{self._name}-{i}"] = task    
                    self._event.set()
                    
                self._workers.clear() # reset workers dict
                self._logger.info.msg("restart-server",widths=3,aligns="^",paddings='=')

        except asyncio.CancelledError:
            if self._msg_worker : cprint(f" + pool ({task_name}) closed",'yellow')
        
    async def pool_join(self):
        await self._work.join()
        print(self._fail._queue)
    # ------------------------------ pool_reset ------------------------------ #
    async def pool_reset(self):
        for i in range(self._n_worker):
            await self._work.put(None)

    # ------------------------------ pool_ready ------------------------------ #
    async def pool_ready(self, msg=True):
        await self._event.wait()
        if msg : self._logger.info.msg(f"taskgroup({self._name}) ready")  
    
    # ------------------------------------------------------------------------ #
    #                                  wrapper                                 #
    # ------------------------------------------------------------------------ #
    def __call__(self, xdef):
        async def wrapper(*args, **kwargs):
            if not self._event.is_set(): cprint("wait for pool_start",color='red')
            await self._event.wait()
            item = Item(xdef=xdef,args=args,kwargs=kwargs)
            await self._work.put(item)
            
        return wrapper



if __name__ == "__main__":
    
    from Qlogger import Logger
    worker = Pooler()
    
    # @worker
    # async def myfun(x):
    #     await asyncio.sleep(1)
    #     print(x)
    #     if x==11:
    #         raise ValueError
    
    # async def main():
    #     asyncio.current_task().set_name('main')

    #     # worker.pool_monitor
    #     sv = asyncio.create_task(worker.pool_start(),name='server')
        
    #     # xt = asyncio.create_task(xtools.xmonitor(reapet=1), name='monitor')

    #     for i in range(20):
    #         await myfun(i)
    #     await asyncio.sleep(3)
    #     await worker.pool_reset()
    #     for i in range(20):
    #         await myfun(i)
        

    #     await sv
    # asyncio.run(main())
    
    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #
    async def myfun(x):
        await asyncio.sleep(1)
        print(x)
        if x==11:
            raise ValueError
    myfun()
    # mfun = worker.apply(myfun)
    
    mfun = worker.deco(myfun)
    mfun()
    mfun()

    async def main():
        asyncio.current_task().set_name('main')
        sv = worker.pool_start()
        # xt = asyncio.create_task(xtools.xmonitor(reapet=1), name='monitor')
        for i in range(20):
            await mfun(i)

        await sv
    asyncio.run(main())