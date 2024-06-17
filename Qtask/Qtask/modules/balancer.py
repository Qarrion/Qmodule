# -------------------------------- ver 240606 -------------------------------- #
# return xdef in set_worker
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove

from functools import wraps
import traceback
import asyncio, uuid
from typing import Callable, Literal

from Qtask.utils.logger_custom import CustomLog
from Qtask.utils.format_time import TimeFormat
from collections import namedtuple

Item = namedtuple('Item', ['future', 'name', 'args', 'kwargs', 'retry'])
import time
class Balancer:

    def __init__(self, name:str='balancer',msg=True):
        """
        + n_worker = 10
        + s_reset = 1
        + n_retry = 3
        + s_restart_remain_empty = 10
        + h_restart_remain_start = 1*60*60
        + traceback = None
        """
        # -------------------------------------------------------------------- #
        CLSNAME = 'Balancer'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)
        # -------------------------------------------------------------------- #
        self._name = name

        # ------------------------------ context ----------------------------- #
        self._xcontext = None
        self._xcontext_type = 'None'
        
        # ------------------------------- main ------------------------------- #
        self._xtask = dict()
        self._queue = asyncio.Queue()
        self._lock = asyncio.Lock()

        # ------------------------------- debug ------------------------------ #
        self._traceback = False

        # ------------------------------ config ------------------------------ #
        self._n_worker = 10
        self._s_reset = 1
        self._limit_type = 'outflow'

        self._n_retry = 3
        self._s_restart_remain_empty = 10
        self._h_restart_remain_start = 1*60*60

    def set_config(self, n_worker=None, s_reset = None, n_retry=None,
                   limit_type:Literal['inflow','outflow','midflow'] = 'outflow',
                   s_restart_remain_empty=None,h_restart_remain_start=None,
                   traceback=None):
        """
        + n_worker = 10
        + s_reset = 1
        + n_retry = 3
        + s_restart_remain_empty = 10
        + h_restart_remain_start = 1*60*60
        + traceback = None
        """
        self.set_config_server(
            n_worker=n_worker,
            s_reset=s_reset,
            n_retry=n_retry,
            limit_type=limit_type,
            traceback=traceback
        )
        self.set_config_manager(
            s_restart_remain_empty=s_restart_remain_empty,
            h_restart_remain_start=h_restart_remain_start)        

    def set_config_server(self,n_worker=None,s_reset=None,n_retry=None,limit_type=None,traceback=None):
        if n_worker is not None: self._n_worker = n_worker
        if s_reset is not None: self._s_reset = s_reset
        if n_retry is not None: self._n_worker = n_retry
        if limit_type is not None: self._limit_type = limit_type
        if traceback is not None: self._traceback = traceback

    def set_config_manager(self, s_restart_remain_empty=None, h_restart_remain_start=None):
        if s_restart_remain_empty is not None: self._s_restart_remain_empty = s_restart_remain_empty
        if h_restart_remain_start is not None: self._h_restart_remain_start = h_restart_remain_start*60*60
    
    # ------------------------------------------------------------------------ #
    #                                  context                                 #
    # ------------------------------------------------------------------------ #
    def set_xcontext(self, xcontext:Callable, with_type:Literal['async_with','async_with_await']='async_with'):
        """ 
        + xcontext = none (default) 
        -> xdef(*arg, **kwargs)
        + xcontext = 'async_with' or 'async_with_await'
        -> xdef(xcontext, *args, **kwargs)"""
        self._xcontext = xcontext
        self._xcontext_type = with_type
        self._custom.info.msg(self._xcontext.__name__, with_type,'')
    
    # ------------------------------------------------------------------------ #
    #                                  server                                  #
    # ------------------------------------------------------------------------ #


    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    # -------------------------------- worker -------------------------------- #
    async def worker(self,xcontext=None,msg_run=False,msg_none=False,msg_limit=False):
        while True:
            item = await self._queue.get()

            # ----------------------------- close ---------------------------- #
            if item is None:
                self._queue.task_done()
                if msg_none:self._custom.info.msg('close',widths=(3,),aligns=("^"),paddings=("."))
                break
            # ---------------------------- process --------------------------- #
            else:
                try:
                    tsp_start = time.time()  #! limiter
                    kwargs=dict() if item.kwargs is None else item.kwargs
                    if msg_run:self._custom.info.msg(item.name, self._xcontext_type, str(item.args))
                    if xcontext is None:
                        result = await asyncio.wait_for(self._xtask[item.name](*item.args, **kwargs),50)
                    else:
                        result = await asyncio.wait_for(self._xtask[item.name](xcontext, *item.args, **kwargs),50)
                    item.future.set_result(result)  
                    

                except asyncio.exceptions.CancelledError as e:
                    task_name = asyncio.current_task().get_name()
                    print(f"\033[33m Interrupted ! in balance ({task_name}) \033[0m")

                except Exception as e:
                    if item.retry < 3:
                        await self._xput_queue_retry(item=item)
                        self._custom.warning.msg(item.name, f'retry({item.retry+ 1})',str(item.args))
                    else:
                        self._custom.error.msg(item.name,'drop', str(item.args))
                        if self._traceback: traceback.print_exc()
                        # traceback.print_exc()
                        raise e
                        # item.future.set_result(e)
                finally:
                    self._queue.task_done()
                    tsp_finish = time.time() #! limiter
                    await self._wait_reset(tsp_start, tsp_finish, msg_limit=msg_limit)
    # ---------------------------------- put --------------------------------- #
    async def _xput_queue(self, name:str, args=(), kwargs:dict=None, retry=0):
        future = asyncio.Future()
        item = Item(future=future,name=name,args=args,kwargs=kwargs,retry=retry)
        async with self._lock:
            await self._queue.put(item)
        return future

    # ----------------------------- put for retry ---------------------------- #
    async def _xput_queue_retry(self, item:Item):
        item = item._replace(retry=item.retry+1)
        async with self._lock:
            await self._queue.put(item)

    # --------------------------------- reset -------------------------------- #
    async def _wait_reset(self, tsp_start:float, tsp_finish, msg_limit=False):
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._s_reset - time.time()
        seconds = max(seconds, 0.0)
        
        if msg_limit :
            msg_sec = TimeFormat.seconds(seconds,'hmsf')
            # msg_ref = TimeFormat.timestamp(tsp_ref,'hmsf')
            self._custom.info.msg('limit',self._limit_type, msg_sec,frame='worker')

        if seconds > 0.0:
            await asyncio.sleep(seconds)

    # ------------------------------------------------------------------------ #
    #                                   fetch                                  #
    # ------------------------------------------------------------------------ #
    def set_xtask(self, xdef):
        # self._custom.info.msg('xdef', f"{xdef.__name__}")
        name = xdef.__name__
        self._xtask[name] = xdef
        return xdef

    async def xfetch(self, name, args=(), kwargs:dict=None):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")
        future = await self._xput_queue(name=name, args=args, kwargs=kwargs)
        result = await future
        return result

    def wrapper(self, func):
        self._custom.info.msg(f"{func.__name__}",'','')
        self.set_xtask(func)
        async def wrapp(*args, **kwargs):
            return await self.xfetch(func.__name__, args, kwargs)
        return wrapp

    # ------------------------------------------------------------------------ #
    #                                    Run                                   #
    # ------------------------------------------------------------------------ #
    # ---------------------------------- run --------------------------------- #
    async def run(self,msg_run=False,msg_done=False,msg_limit=False):
        tasks = [
            asyncio.create_task(self.server(msg_run=msg_run,msg_done=msg_done,msg_limit=msg_limit),name=f"{self._name}-S"),
            asyncio.create_task(self.manager(),name=f"{self._name}-M"),
        ]
        await asyncio.gather(*tasks)
    
    # -------------------------------- server -------------------------------- #
    async def server(self,msg_run=False,msg_done=False,msg_limit=False):
        while True:
            if self._xcontext_type == "async_with":
                 async with self._xcontext() as xcontext:
                    async with asyncio.TaskGroup() as tg:
                        for i in range(self._n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_done,msg_limit),name=f"{self._name}-{i+1}")
            
            elif self._xcontext_type == "async_with_await":
                async with await self._xcontext() as xcontext:
                    async with asyncio.TaskGroup() as tg:
                        for i in range(self._n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_done,msg_limit),name=f"{self._name}-{i+1}")

            else:
                async with asyncio.TaskGroup() as tg:
                    for i in range(self._n_worker):
                        tg.create_task(self.worker(None,msg_run,msg_done,msg_limit),name=f"{self._name}-{i+1}")

            self._custom.debug.msg('restart',widths=(3,),aligns=("^"),paddings=("."))
    # -------------------------------- manager ------------------------------- #
    async def manager(self):
        loop = asyncio.get_event_loop()
        # -------------------------------------------------------------------- #
        while True:
            tasks_started = False
            tasks_done = False

            time_tasks_started = loop.time()
            # ---------------------------------------------------------------- #
            while True:
                if self._queue._unfinished_tasks > 0:
                    tasks_started = True

                if tasks_started and self._queue._unfinished_tasks == 0:
                    time_tasks_done = loop.time()
                    # -------------------------------------------------------- #
                    while self._queue._unfinished_tasks == 0:
                        await asyncio.sleep(0.5)
                        is_restart_done = loop.time() - time_tasks_done >= self._s_restart_remain_empty
                        is_restart_started = loop.time() - time_tasks_started >= self._h_restart_remain_start
                        if is_restart_done and is_restart_started:
                            async with self._lock:
                                for _ in range(self._n_worker): await self._queue.put(None)
                            tasks_done = True
                    # -------------------------------------------------------- #
                            
                if tasks_done:
                    break
                else:
                    await asyncio.sleep(0.5)
        # -------------------------------------------------------------------- #
    # ------------------------------------------------------------------------ #



if __name__ == "__main__":
    import httpx
    balance = Balancer()
    balance.set_xcontext(httpx.AsyncClient)
    balance.set_config(h_restart_remain_start=0,n_worker=5)

    @balance.wrapper
    async def asleep(xcontext:httpx.AsyncClient, sec:int):
        # await asyncio.sleep(1) 
        r = await xcontext.get('https://www.naver2.com/')
        return r


    # async def main():
    #     asyncio.create_task(balance.run(True,True,True)),
    #     await asleep(sec=1)
        # await asleep(sec=1)
        # await asleep(sec=1)

    async def xclient():
        tasks = [
            asleep(sec=1),
            asleep(sec=1),
            asleep(sec=1),
            ]
        await asyncio.gather(*tasks)
        
 
    async def main():
        tasks=[
            asyncio.create_task(balance.run(True,True,True)),
            asyncio.create_task(xclient()),
        ]
        await asyncio.gather(*tasks)


    asyncio.run(main())


