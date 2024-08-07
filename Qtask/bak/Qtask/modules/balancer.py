 # -------------------------------- ver 240606 -------------------------------- #
# return xdef in set_worker
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove
# -------------------------------- ver 240623 -------------------------------- #
# mode_unlimit
# ---------------------------------------------------------------------------- #

from functools import wraps
import re
import traceback
import asyncio, uuid
from typing import Callable, Literal

import time

from Qtask.utils.logger_custom import CustomLog
from Qtask.utils.format_time import TimeFormat
from Qtask.utils.print_color import cprint

from collections import namedtuple

Item = namedtuple('Item', ['future', 'name', 'args', 'kwargs', 'retry'])
import time
class Balancer:

    def __init__(self, name:str='balancer',msg=True):
        """
        + n_worker = 10
        + s_reset = 1
        + n_retry = 3
        + s_remain_empty = 10
        + h_remain_start = 2*60*60
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
        self._is_server_on = False
        # ------------------------------ context ----------------------------- #
        self._xcontext = None
        self._xcontext_type = 'None'
        
        # ------------------------------- main ------------------------------- #
        self._xtask = dict()
        self._queue = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore()
        
        # ------------------------------- debug ------------------------------ #
        self._traceback = False
        self._msg_wrapper = False
        self._limit = True

        # ------------------------------ config ------------------------------ #
        self._n_worker = 10
        self._s_reset = 1
        self._limit_type = 'outflow'
        self._n_retry = 3

        self._s_remain_empty = 10
        self._s_remain_start = 2*60*60
        self._is_restart = True
        self._is_empty = True

        # ------------------------------ refresh ----------------------------- #
        self._semaphore = asyncio.Semaphore(self._n_worker)

    #! ------------------------------------------------------------------------ #
    #!                                  setter                                  #
    #! ------------------------------------------------------------------------ #

    def set_config(self, n_worker=None, s_reset = None, n_retry=None,
                   limit_type:Literal['inflow','outflow','midflow'] = 'outflow',
                   s_remain_empty=None,s_remain_start=None,
                   traceback=None, msg_wrapper=None):
        """
        + n_worker = 10
        + s_reset = 1
        + n_retry = 3
        + limit_type['inflow','outflow','midflow'] = 'out_flow'
        + traceback = None

        + s_remain_empty = 10
        + h_restart_remain_start = 1*60*60
        + msg_wrapper = False
        """
        if msg_wrapper is not None: self._msg_wrapper = msg_wrapper

        self.set_config_server(
            n_worker=n_worker,
            s_reset=s_reset,
            n_retry=n_retry,
            limit_type=limit_type,
            traceback=traceback
        )
        self.set_config_manager(
            s_remain_empty=s_remain_empty,
            s_remain_start=s_remain_start)        


    def set_config_server(self,n_worker=None,s_reset=None,n_retry=None,limit_type=None,traceback=None):
        """
        + n_worker = 10
        + s_reset = 1
        + n_retry = 3
        + limit_type['inflow','outflow','midflow'] = 'out_flow'
        + traceback = None
        """
        if n_worker is not None: self._n_worker = n_worker
        if s_reset is not None: self._s_reset = s_reset
        if n_retry is not None: self._n_retry = n_retry
        if limit_type is not None: self._limit_type = limit_type
        if traceback is not None: self._traceback = traceback
        self._semaphore = asyncio.Semaphore(self._n_worker)

    def set_config_manager(self, s_remain_empty=None, s_remain_start=None):
        """+ s_remain_empty = 10
            + s_restart_remain_start = 1*60*60"""
        if s_remain_empty is not None: self._s_remain_empty = s_remain_empty
        if s_remain_start is not None: self._s_remain_start = s_remain_start
    
    def set_mode_once(self, after_remain_n_second_empty:int = 5):
        self._is_restart = False
        self._s_remain_start = 0
        self._s_remain_empty = after_remain_n_second_empty

    def set_mode_unlimit(self):
        self._limit = False

    def get_load(self):
        return self._n_worker - self._semaphore._value

    #! ------------------------------------------------------------------------ #
    #!                                  context                                 #
    #! ------------------------------------------------------------------------ #
    def set_xcontext(self, xcontext:Callable, with_type:Literal['async_with','async_with_await']='async_with',msg=False):
        """ 
        + xcontext = none (default) 
        -> xdef(*arg, **kwargs)
        + xcontext = 'async_with' or 'async_with_await'
        -> xdef(xcontext, *args, **kwargs)"""
        self._xcontext = xcontext
        self._xcontext_type = with_type
        if msg : self._custom.info.msg(self._xcontext.__name__, with_type)

    #! ------------------------------------------------------------------------ #
    #!                                  worker                                  #
    #! ------------------------------------------------------------------------ #
    # -------------------------------- worker -------------------------------- #
    async def worker(self,xcontext=None,msg_run=False,msg_close=False,msg_limit=False):
        task_name = asyncio.current_task().get_name()
        while True:
            item = await self._queue.get()
            async with self._semaphore:
                #! ------------------------------------------------------------ #
                # print(f"[i n] balancer({self._name}), remain({self._semaphore._value}/{self._n_worker})")
                #! ------------------------------------------------------------ #
                self._is_empty = False # for manager
                # ----------------------------- close ---------------------------- #
                if item is None:
                    self._queue.task_done()
                    if msg_close:self._custom.info.msg('close',widths=(3,),aligns=("^"),paddings=("."))
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
                        
                        cprint(f" - worker ({task_name}) closed",'yellow')
                        # print(f"\033[33m Interrupted ! in balance ({task_name}) \033[0m")

                    except Exception as e:
                        if item.retry < self._n_retry:
                            # ---------------------------------------------------- #
                            # print(self._s_reset*(item.retry+1)/(self._n_retry*5))
                            # ---------------------------------------------------- #
                            buffer = round(self._s_reset*(item.retry/self._n_retry),3)
                            await asyncio.sleep(buffer)
                            await self._xput_queue_retry(item=item)
                            self._custom.warning.msg(item.name, f'retry({item.retry+ 1})',f"buff({buffer})")
                        else:
                            self._custom.error.msg(item.name,'drop', str(item.args))
                            if self._traceback: traceback.print_exc()

                            #! for break execute
                            item.future.set_result(e) 
                            raise e
                            # traceback.print_exc()
                    finally:
                        tsp_finish = time.time() #! limiter
                        if self._limit : await self._wait_reset(tsp_start, tsp_finish, msg_limit=msg_limit)
                        self._queue.task_done()
            # print(f"[out] balancer({self._name}), remain({self._semaphore._value}/{self._n_worker})")

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

    #! ------------------------------------------------------------------------ #
    #!                                   fetch                                  #
    #! ------------------------------------------------------------------------ #
    def set_xtask(self, xdef):
        name = xdef.__name__
        self._xtask[name] = xdef
        return xdef

    async def xfetch(self, name, args=(), kwargs:dict=None):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")
        if not self._is_server_on:
            print(f"\033[31m balancer.server for {name}() is not running [{self._name}] \033[0m")
        future = await self._xput_queue(name=name, args=args, kwargs=kwargs)
        result = await future
        return result

    def wrapper(self, func):      
        if self._msg_wrapper : self._custom.info.msg(f"{func.__name__}")
        self.set_xtask(func)
        async def wrapp(*args, **kwargs):
            return await self.xfetch(func.__name__, args, kwargs)
        return wrapp

    #! ------------------------------------------------------------------------ #
    #!                                    Run                                   #
    #! ------------------------------------------------------------------------ #
    # ---------------------------------- run --------------------------------- #
    #*| candle-1......worker | xget_candle  , async_with   , ()            |*#
    async def run(self,msg_run=False,msg_restart=False,msg_close=False,msg_limit=False,return_excetion=False,msg_time=False):
        try:
            tasks = [
                asyncio.create_task(self.server(
                                        msg_restart=msg_restart,
                                        msg_run=msg_run,
                                        msg_close=msg_close,
                                        msg_limit=msg_limit
                                        ),
                                        name=f"{self._name}-S"),
                asyncio.create_task(self.manager(msg_time=msg_time),name=f"{self._name}-M"),
            ]
            await asyncio.gather(*tasks,return_exceptions=return_excetion)
        except asyncio.exceptions.CancelledError:
            task_name = asyncio.current_task().get_name()
            cprint(f" - balancer ({task_name}) closed",'yellow')
    
    # -------------------------------- server -------------------------------- #
    async def server(self,msg_run=False,msg_restart=False,msg_close=False,msg_limit=False):
        self._is_server_on = True
        # print(f"\033[31m [{self._name}] start \033[0m")
        while True:
            if self._xcontext_type == "async_with":
                async with self._xcontext() as xcontext:
                    async with asyncio.TaskGroup() as tg:
                        for i in range(self._n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_close,msg_limit),
                                            name=f"{self._name}-{i}")
            
            elif self._xcontext_type == "async_with_await":
                async with await self._xcontext() as xcontext:
                    async with asyncio.TaskGroup() as tg:
                        for i in range(self._n_worker):
                            tg.create_task(self.worker(xcontext,msg_run,msg_close,msg_limit),
                                            name=f"{self._name}-{i}")

            else:
                async with asyncio.TaskGroup() as tg:
                    for i in range(self._n_worker):
                        tg.create_task(self.worker(None,msg_run,msg_close,msg_limit),
                                        name=f"{self._name}-{i}")
            
            if self._is_restart:
                if msg_restart : self._custom.debug.msg('restart',aligns=("^"),paddings=("."))
            else:
                print(f"\033[31m [{self._name}] terminate server \033[0m")
                break
    
    # -------------------------------- manager ------------------------------- #
    async def manager(self,msg_time=False):

        is_restart = True
        while is_restart:
        # -------------------------------------------------------------------- #
            time_start = time.time()

            is_timeover = False
            while not is_timeover:
            # ---------------------------------------------------------------- #
                time_empty = time.time()

                is_empty = True
                while is_empty:
                # ------------------------------------------------------------ #
                    await asyncio.sleep(0.5)

                    sec_empty = time.time() - time_empty; sec_start = time.time() - time_start 
                    #! -------------------------------------------------------- #
                    if msg_time: self._custom.debug.msg(
                        f"{sec_empty >= self._s_remain_empty} {round(sec_empty,2)}",
                        f"{sec_start >= self._s_remain_start:} {round(sec_start,2)}")
                    #! -------------------------------------------------------- #
                    if (sec_empty >= self._s_remain_empty and sec_start >= self._s_remain_start) or \
                        (sec_start >= self._s_remain_start * 2):
        
                        async with self._lock:
                            for _ in range(self._n_worker): await self._queue.put(None)

                        is_empty = False
                        is_timeover = True
                        is_restart = self._is_restart
                    else:
                        is_empty = self._is_empty; self._is_empty=True
                        is_timeover= False

                # ------------------------------------------------------------ #
            # ---------------------------------------------------------------- #
            await asyncio.sleep(0.5)
        # -------------------------------------------------------------------- #



if __name__ == "__main__":

    import httpx
    balance = Balancer()
    balance.set_xcontext(httpx.AsyncClient)
    balance.set_config_manager(s_remain_empty=10, s_remain_start=20)
    # balance.set_config(s_restart_remain_start=0,n_worker=10)

    @balance.wrapper
    async def asleep(xcontext:httpx.AsyncClient, sec:int):
        await asyncio.sleep(sec) 
        r = await xcontext.get('https://www.naver.com/')
        print('do')
        return r
    
    @balance.wrapper
    async def req(xcontext:httpx.AsyncClient):
        r = await xcontext.get('https://www.naver.com/')
        print('do')
        return r
    
    async def loop():
        while True:
            await asyncio.sleep(5)
            await req()


    # async def main():
    #     asyncio.create_task(balance.run(True,True,True)),
    #     await asleep(sec=1)
        # await asleep(sec=1)
        # await asleep(sec=1)

    # async def xclient():
    #     # await asyncio.sleep(1)
    #     tasks=[
    #         asyncio.create_task(req(),name=f"t-{i}") for i in range(11)
    #     ]
    #     await asyncio.gather(*tasks)
        
 
    async def main():
        tasks=[
            asyncio.create_task(balance.run(True,True,True,msg_time=True)),
            # asyncio.create_task(xclient()),
            asyncio.create_task(loop()),
        ]
        
        await asyncio.gather(*tasks)


    asyncio.run(main())


