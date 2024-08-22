# -------------------------------- ver 240606 -------------------------------- #
# return xdef in set_worker
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove

from functools import wraps
import asyncio, uuid
from typing import Callable, Literal

from Qtask.utils.logger_custom import CustomLog
from collections import namedtuple

Item = namedtuple('Item', ['future', 'name', 'args', 'kwargs', 'retry'])
import time
class Balance:

    def __init__(self, name:str='balance',msg=True):
        CLSNAME = 'Balance'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,CLSNAME,'async')
        if msg : self._custom.info.msg(name)

        self.i_queue = asyncio.Queue()
        self._xworkers = dict()
        self._xcontext = None
        self._lock = asyncio.Lock()
        self._status='stop'
        self._async_context = None

        # ------------------------------ config ------------------------------ #
        self._n_retry = 3
        self._n_reconnect = 60

    # xdef:Callable [x] -> interferes with displaying function information in the IDE 
    def set_xworker(self, xdef, name:str=None):
        self._custom.info.msg('xdef', xdef.__name__)
        if name is None:
            name = xdef.__name__
        self._xworkers[name] = xdef
        return xdef

    def set_xcontext(self, xcontext:Callable, with_type:Literal['async_with','async_with_await']='async_with'):
        """ + with xbalance
        + xdef(xcontext, args, kwargs)"""
        self._xcontext = xcontext
        if with_type == 'async_with':
            self._async_context = self._async_with
        elif with_type =='async_with_await':
            self._async_context = self._async_with_await
        else:
            self._async_context = None

    def _debug_workers(self):
        print(self._xworkers.keys())
    # ------------------------------------------------------------------------ #
    #                                    run                                   #
    # ------------------------------------------------------------------------ #
    async def _xput_i_queue(self, name:str, args=(), kwargs:dict=None, retry=0):
        future = asyncio.Future()
        item = Item(future=future,name=name,args=args,kwargs=kwargs,retry=retry)
        await self.i_queue.put(item)
        return future

    async def _xrun_work(self,item:Item, xcontext=None, msg=True):
        if await self._is_starting():
            text = item.name if xcontext is None else f"{item.name}_with_{xcontext.__class__.__name__}"
            if msg : self._custom.info.msg('task', self._custom.arg(text,3,'l',"-"), frame='balance')

        kwargs=dict() if item.kwargs is None else item.kwargs
        try:
            if xcontext is None:
                result = await asyncio.wait_for(self._xworkers[item.name](*item.args, **kwargs),50)
            else:
                result = await asyncio.wait_for(self._xworkers[item.name](xcontext, *item.args, **kwargs),50)

        except asyncio.exceptions.CancelledError as e:
            task_name = asyncio.current_task().get_name()
            print(f"\033[33m Interrupted ! in balance ({task_name}) \033[0m")

        except Exception as e:
            if item.retry < 3:
                await self._xput_i_queue(
                    name=item.name, args=item.args, kwargs=item.kwargs, retry=item.retry +1)
            else:
                result = None
                print(e)
        finally:
            self.i_queue.task_done()
            if not item.future.cancelled():
                item.future.set_result(result)

            if await self._is_stopping():
                text = item.name if xcontext is None else f"{item.name}_with_{xcontext.__class__.__name__}"
                if msg : self._custom.info.msg('task', self._custom.arg(text,3,'r',"-"), frame='balance')
            
    # ------------------------------------------------------------------------ #
    #                                  server                                  #
    # ------------------------------------------------------------------------ #
    async def xrun(self):
        while True:
            item:Item = await self.i_queue.get()
            asyncio.create_task(self._xrun_work(item))

    async def xrun_with_xcontext(self):
        await self._async_context()

    # ------------------------------------------------------------------------ #
    #                                    sub                                   #
    # ------------------------------------------------------------------------ #
    async def _async_with_await(self):
        #! sql
        while True:
            async with await self._xcontext() as xcontext:
                self._custom.info.msg('serve', 'reconnect', frame='xrun_with')
                while True:
                    try:
                        item:Item = await asyncio.wait_for(self.i_queue.get(),timeout=self._n_reconnect)
                        asyncio.create_task(self._xrun_work(item, xcontext))
                    except asyncio.TimeoutError:
                        if await self._is_stopped():
                            break
                        else:
                            pass

    async def _async_with(self):
        #! api
        while True:
            async with self._xcontext() as xcontext:
                self._custom.info.msg('serve', 'reconnect', frame='xrun_with')
                while True:
                    try:
                        item:Item = await asyncio.wait_for(self.i_queue.get(),timeout=self._n_reconnect)
                        asyncio.create_task(self._xrun_work(item, xcontext))
                    except asyncio.TimeoutError:
                        if await self._is_stopped():
                            break
                        else:
                            pass
                    
    # ------------------------------------------------------------------------ #
    #                                  status                                  #
    # ------------------------------------------------------------------------ #
    async def _is_starting(self):
        async with self._lock:
            if self.i_queue._unfinished_tasks != 0 and self._status=='stop':
                self._status = 'start'
                return 1
            else:
                return 0
            
    async def _is_stopping(self):
        async with self._lock:
            if self.i_queue._unfinished_tasks == 0 and self._status=='start':
                self._status = 'stop'
                # print(time.time()-self.a)
                return 1
            else:
                return 0
            
    async def _is_stopped(self):
        async with self._lock:
            if self.i_queue._unfinished_tasks == 0 and self._status=='stop':
                return 1
            else:
                return 0
    # ------------------------------------------------------------------------ #
    #                                   fetch                                  #
    # ------------------------------------------------------------------------ #
    async def xfetch(self, name, args=(), kwargs:dict=None):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")
        future = await self._xput_i_queue(name=name, args=args, kwargs=kwargs)
        result = await future
        return result

if __name__ == "__main__":
    import httpx
    # async def asleep(sec:int):
    async def asleep(context, sec:int):
        print(f"s---{sec}")
        await asyncio.sleep(sec) 
        print(f"e---{sec}")
        return sec

    sv = Balance()
    sv.set_xworker(asleep)
    sv.set_xcontext(httpx.AsyncClient)
    
    # async def work():
    #     tasks = [
    #         asyncio.create_task( sv.xfetch('asleep', (1,))),
    #         asyncio.create_task( sv.xfetch('asleep', (2,))),
    #         asyncio.create_task( sv.xfetch('asleep', (3,)))
    #     ]
    #     await asyncio.gather(*tasks)

    async def works():
        aa = await sv.xfetch('asleep', (2,))
        print(aa)
        bb = await  sv.xfetch('asleep', (2,))
        print(bb)
        cc = await  sv.xfetch('asleep', (3,))
        print(cc)

    async def main():

        tasks = [
            asyncio.create_task(sv.xrun_with_xcontext()),
            asyncio.create_task(works()),

        ]

        await asyncio.gather(*tasks)

    asyncio.run(main())
