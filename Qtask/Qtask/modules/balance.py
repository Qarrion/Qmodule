import asyncio, uuid
from typing import Callable, Literal
import httpx
from Qtask.utils.logger_custom import CustomLog
from collections import namedtuple

Item = namedtuple('Item', ['future', 'name', 'args', 'kwargs', 'retry'])
import time
class Balance:

    def __init__(self, name:str='balance',msg=True):
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,'async')
        if msg : self._custom.info.msg('Balance',name)

        self.i_queue = asyncio.Queue()
        self._xworkers = dict()
        self._xcontext = None
        self._lock = asyncio.Lock()
        self._status='stop'

        # ------------------------------ config ------------------------------ #
        self._n_retry = 3
        self._n_reconnect = 60

    def set_xworker(self, xdef:Callable, name:str=None):
        self._custom.info.msg('xdef', xdef.__name__)
        if name is None:
            name = xdef.__name__
        self._xworkers[name] = xdef

    def set_xcontext(self, xcontext:Callable):
        """ 
        + with xbalance
        + xdef(xcontext, args, kwargs)"""
        self._xcontext = xcontext

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

        except Exception as e:
            if item.retry < 3:
                await self._xput_i_queue(
                    name=item.name, args=item.args, kwargs=item.kwargs, retry=item.kwargs+1)
            else:
                result = None
                item.future.set_result(result)
        finally:
            self.i_queue.task_done()

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

    # ------------------------------------------------------------------------ #
    #                                    sub                                   #
    # ------------------------------------------------------------------------ #
    async def xrun_with_await_xcontext(self):
        while True:
            async with await self._xcontext() as xcontext:
                print('reconnect')
                while True:
                    try:
                        item:Item = await asyncio.wait_for(self.i_queue.get(),timeout=self._n_reconnect)
                        asyncio.create_task(self._xrun_work(item, xcontext))
                    except asyncio.TimeoutError:
                        if await self._is_stopped():
                            break
                        else:
                            pass

    async def xrun_with_xcontext(self):
        while True:
            async with self._xcontext() as xcontext:
            # async with httpx.AsyncClient() as xcontext:
                print('reconnect')
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
        future = await self._xput_i_queue(name=name, args=args, kwargs=kwargs)
        return future


if __name__ == "__main__":

    # async def asleep(sec:int):
    async def asleep(context, sec:int):
        print(f"s---{sec}")
        await asyncio.sleep(sec) 
        print(f"e---{sec}")
        return sec

    sv = Balance()
    sv.set_xworker(asleep)

    sv.set_xcontext(httpx.AsyncClient)
    
    async def work():

        tasks = [
            asyncio.create_task( sv.xfetch('asleep', (1,))),
            asyncio.create_task( sv.xfetch('asleep', (2,))),
            asyncio.create_task( sv.xfetch('asleep', (3,)))
        ]

        await asyncio.gather(*tasks)

    async def works():
        await  sv.xfetch('asleep', (1,))
        await  sv.xfetch('asleep', (2,))
        await  sv.xfetch('asleep', (3,))

    async def main():

        tasks = [
            # asyncio.create_task(sv.xrun()),
            asyncio.create_task(sv.xrun_with_xcontext()),
            # asyncio.create_task(sv.xrun_with_xclient()),

            asyncio.create_task(works()),

        ]

        await asyncio.gather(*tasks)



    asyncio.run(main())

    # httpx.AsyncClient()