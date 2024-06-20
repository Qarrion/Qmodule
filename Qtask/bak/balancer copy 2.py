# -------------------------------- ver 240606 -------------------------------- #
# return xdef in set_worker
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove

from functools import wraps
import traceback
import asyncio, uuid
from typing import Callable, Literal

from Qtask.utils.logger_custom import CustomLog
from collections import namedtuple

Item = namedtuple('Item', ['future', 'name', 'args', 'kwargs', 'retry'])
import time
class Balancer:

    def __init__(self, name:str='balance',msg=True):
        """
        + n_retry = 3
        + n_worker = 10
        + s_restart_remain_empty = 10
        + h_restart_remain_start = 1*60*60
        """
        CLSNAME = 'Balancer'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.msg(name)

        self._xcontext = None
        self._xcontext_type = None
        self._xtask = dict()
        
        self._queue = asyncio.Queue()
        self._lock = asyncio.Lock()

        self._status='stop'
        self._traceback = False
        # ------------------------------ config ------------------------------ #
        self._n_retry = 3
        self._n_worker = 10
        self._s_restart_remain_empty = 10
        self._h_restart_remain_start = 1*60*60

    def set_config(self, n_worker=None, n_retry=None,
                   s_restart_remain_empty=None,h_restart_remain_start=None,
                   traceback=None):
        if n_worker is not None: self._n_worker = n_worker
        if n_retry is not None: self._n_worker = n_retry
        if s_restart_remain_empty is not None: self._s_restart_remain_empty = s_restart_remain_empty
        if h_restart_remain_start is not None: self._h_restart_remain_start = h_restart_remain_start*60*60
        if traceback is not None: self._traceback = traceback
    
    def set_xtask(self, xdef, name:str=None):
        self._custom.info.msg('xdef', f"{xdef.__name__}")

        if name is None:
            name = xdef.__name__
        self._xtask[name] = xdef
        return xdef

    def set_xcontext(self, xcontext:Callable, with_type:Literal['async_with','async_with_await']='async_with'):
        """ + with xbalance
        + xdef(xcontext, args, kwargs)"""
        self._xcontext = xcontext
        self._xcontext_type = with_type

    def debug_xtasks(self):
        print(self._xtask.keys())

    # ------------------------------------------------------------------------ #
    #                                   fetch                                  #
    # ------------------------------------------------------------------------ #
    async def _xput_queue(self, name:str, args=(), kwargs:dict=None, retry=0):
        future = asyncio.Future()
        item = Item(future=future,name=name,args=args,kwargs=kwargs,retry=retry)
        async with self._lock:
            await self._queue.put(item)
        return future
    
    async def _xput_queue_retry(self, item:Item):
        item = item._replace(retry=item.retry+1)
        async with self._lock:
            await self._queue.put(item)

    async def xfetch(self, name, args=(), kwargs:dict=None):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")
        future = await self._xput_queue(name=name, args=args, kwargs=kwargs)
        result = await future
        return result

    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    async def worker(self,xcontext=None,msg_run=False,msg_done=False):
        while True:
            item = await self._queue.get()

            if item is None:
                # p("shutting down.")
                self._queue.task_done()
                if msg_done:self._custom.info.msg('close',frame='task')
                break
            else:
                try:
                    kwargs=dict() if item.kwargs is None else item.kwargs
                    if xcontext is None:
                        result = await asyncio.wait_for(self._xtask[item.name](*item.args, **kwargs),50)
                        if msg_run:self._custom.info.msg('xfetch',item.name, self._xcontext_type, frame='task')
                    else:
                        result = await asyncio.wait_for(self._xtask[item.name](xcontext, *item.args, **kwargs),50)
                        if msg_run:self._custom.info.msg('xfetch',item.name, self._xcontext_type, frame='task')
                    item.future.set_result(result)  
                except asyncio.exceptions.CancelledError as e:
                    task_name = asyncio.current_task().get_name()
                    print(f"\033[33m Interrupted ! in balance ({task_name}) \033[0m")

                except Exception as e:
                    if item.retry < 3:
                        await self._xput_queue_retry(item=item)
                        self._custom.warning.msg('except',item.name, f'retry({item.retry+ 1})',frame='task')
                    else:
                        self._custom.error.msg('drop',item.name, str(item.args), frame='task')
                        item.future.set_result(e)
                        if self._traceback: traceback.print_exc()
                finally:
                    self._queue.task_done()


    # ------------------------------------------------------------------------ #
    #                                    Run                                   #
    # ------------------------------------------------------------------------ #
    # ---------------------------------- run --------------------------------- #
    async def run(self,n_worker:int=None,msg_run=False,msg_done=False):
        tasks = [
            asyncio.create_task(self.server(n_worker=n_worker,msg_run=msg_run,msg_done=msg_done)),
            asyncio.create_task(self.manager()),
        ]
        await asyncio.gather(*tasks)
    # -------------------------------- server -------------------------------- #
    async def server(self,n_worker:int=None,msg_run=False,msg_done=False):
        n_worker = self._n_worker if n_worker is None else n_worker

        while True:
            if self._xcontext_type == "async_with":
                 async with self._xcontext() as xcontext:

                    async with asyncio.TaskGroup() as tg:
                        for i in range(n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_done),name=f"worker-{i+1}")
            
            elif self._xcontext_type == "async_with_await":
                async with await self._xcontext() as xcontext:

                    async with asyncio.TaskGroup() as tg:
                        for i in range(n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_done),name=f"worker-{i+1}")

            else:
                async with asyncio.TaskGroup() as tg:
                    for i in range(n_worker):
                        tg.create_task(self.worker(None,msg_run),name=f"worker-{i+1}")

            self._custom.debug.msg('restart')
    
    # -------------------------------- manager ------------------------------- #
    async def manager(self):
        loop = asyncio.get_event_loop()
        # ------------------------------------------------------------------------ #
        while True:
            tasks_started = False
            tasks_done = False

            time_tasks_started = loop.time()
            # -------------------------------------------------------------------- #
            while True:
                if self._queue._unfinished_tasks > 0:
                    tasks_started = True

                if tasks_started and self._queue._unfinished_tasks == 0:
                    time_tasks_done = loop.time()
                    # ------------------------------------------------------------ #
                    while self._queue._unfinished_tasks == 0:
                        await asyncio.sleep(0.5)
                        is_restart_done = loop.time() - time_tasks_done >= self._s_restart_remain_empty
                        is_restart_started = loop.time() - time_tasks_started >= self._h_restart_remain_start
                        if is_restart_done and is_restart_started:
                            async with self._lock:
                                for _ in range(self._n_worker): await self._queue.put(None)
                            tasks_done = True
                    # ------------------------------------------------------------ #
                if tasks_done:
                    break
                else:
                    await asyncio.sleep(0.5)
        # -------------------------------------------------------------------- #
    # ------------------------------------------------------------------------ #

    def wrapper(self, func):
        self.set_xtask(func)

        async def wrapp(*args, **kwargs):
            return await self.xfetch(func.__name__, args, kwargs)

        return wrapp

if __name__ == "__main__":
    import httpx


    balance = Balancer()
    # balance.set_xtask(asleep)
    balance.set_xcontext(httpx.AsyncClient)
    balance.set_config(h_restart_remain_start=0)


    @balance.wrapper
    async def asleep(xcontext:httpx.AsyncClient, sec:int):
        await asyncio.sleep(1) 
        r = await xcontext.get('https://www.naver.com/')
        return r


    # async def main():
    #     asyncio.create_task(balance.run(5,True,True)),
    #     await asleep(sec=1)
    #     await asleep(sec=1)
    #     await asleep(sec=1)

    async def xclient():
        tasks = [
            asleep(sec=1),
            asleep(sec=1),
            asleep(sec=1),
            asleep(sec=1),
            asleep(sec=1),
            ]
        
        await asyncio.gather(*tasks)
 
    async def main():
        tasks=[
            asyncio.create_task(balance.run(5,True,True)),
            asyncio.create_task(xclient()),
        ]
        await asyncio.gather(*tasks)


    asyncio.run(main())
