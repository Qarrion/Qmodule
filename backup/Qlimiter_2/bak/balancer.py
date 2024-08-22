import asyncio
from collections import namedtuple
from re import T
import time
import traceback
from typing import Callable, Literal
from Qlimiter.utils.logger_custom import CustomLog
from Qlimiter.modules.session import Xsession
from Qlimiter.utils.print_color import cprint
from Qlimiter.utils.format_time import TimeFormat

item_xfetch = namedtuple('item_xfetch', ['future', 'name', 'args', 'kwargs', 'retry'])
item_xthrow = namedtuple('item_xthrow', ['name', 'args', 'kwargs', 'retry'])

class Balancer:

    def __init__(self, name:str='balancer', msg=True):
        """
        >>> # 
        balancer = Balancer()
        balancer.set_config()
        balancer.set_xsession()
        """
        # -------------------------------------------------------------------- #
        CLSNAME = 'Balancer'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = CustomLog.getlogger(name=name)
            print(f"\033[31m No Module Qlogger \033[0m")
        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        # -------------------------------------------------------------------- #
        self.xsession = None
        self.xdefs:dict = dict()

        self._queue = asyncio.Queue()
        self._lock = asyncio.Lock()

        self._name = name
        self._is_server_on = False
        # -------------------------------------------------------------------- #

    def set_config(self, n_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'],
        n_retry=3, msg_traceback=False, msg_debug=False, msg_wrapper=False):

        self._n_worker = n_worker
        self._seconds = seconds
        self._limit_type = limit

        self._msg_traceback = msg_traceback
        self._msg_debug = msg_debug
        self._msg_wrapper = msg_wrapper

        self._semaphore = asyncio.Semaphore(n_worker)

        self._n_retry = n_retry
        self._custom.info.msg(limit,f"max({n_worker})",f"sec({seconds})" )

    def set_xsession(self, xconnector:Callable, close_method:str, close_status:str):
        """>>> # used case 
        set_xsession(xconnector = httpx.AsyncClient, close_method='aclose', close_status='is_closed')
        set_xsession(xconnector = pgsql.xconnect_pool, close_method='close', close_status='closed')"""
        self.xsession = Xsession(xconnector, close_method, close_status) 
        self.xsession.start()
        self._custom.info.msg(self.xsession.xconn.__class__.__name__,close_method, close_status)
        
    # ------------------------------------------------------------------------ #
    #                                  wrapper                                 #
    # ------------------------------------------------------------------------ #
    def wrapper_xfetch(self, xdef):      
        if self._msg_wrapper : self._custom.info.msg(f"{xdef.__name__}")
        self.set_xdef(xdef)

        async def wrapper(*args, **kwargs):
            return await self.xfetch(xdef, args, kwargs)
        return wrapper

    def wrapper_xthrow(self, xdef):      
        if self._msg_wrapper : self._custom.info.msg(f"{xdef.__name__}")
        self.set_xdef(xdef)
        async def wrapper(*args, **kwargs):
            return await self.xthrow(xdef, args, kwargs)
        return wrapper
    
    def set_xdef(self,xdef):
        self.xdefs[xdef.__name__] = xdef
        return xdef
    
    async def xfetch(self, xdef, args=(), kwargs:dict=None):
        name = xdef.__name__
        self._assert_produce(args=args,name=name)
        future = asyncio.Future()
        retry = 0

        item = item_xfetch(future=future,name=name,args=args,kwargs=kwargs,retry=retry)
        async with self._lock:
            await self._queue.put(item)

        result = await future
        return result
    
    async def xthrow(self, xdef, args=(), kwargs:dict=None):
        name = xdef.__name__
        self._assert_produce(args=args,name=name)
        retry = 0
        item = item_xthrow(name=name,args=args,kwargs=kwargs,retry=retry)
        async with self._lock:
            await self._queue.put(item)

        return None

    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    async def worker(self, msg_close=False):
        task_name = asyncio.current_task().get_name()

        while True:
            item = await self._queue.get()
            async with self._semaphore:
                if item is None:
                    self._queue.task_done()
                    if msg_close:self._custom.info.msg('close',widths=(3,),aligns=("^"),paddings=("."))
                    break
                else:
                    try:
                        tsp_start = time.time()  #! limiter
                        kwargs=dict() if item.kwargs is None else item.kwargs
                        if self._msg_debug: 
                            self._custom.info.msg('start',TimeFormat.timestamp(tsp_start,'hmsf'),frame='',aligns=("<","<"), paddings=("","-")) 

                        if self.xsession is not None:
                            result = await asyncio.wait_for(self.xdefs[item.name](self.xsession.xconn, *item.args, **kwargs),50)
                        else:
                            result = await asyncio.wait_for(self.xdefs[item.name](*item.args, **kwargs),50)

                        if item.__class__.__name__ == "item_xfetch":
                            item.future.set_result(result)  
                        
                    except asyncio.exceptions.CancelledError as e:
                        cprint(f" - worker ({task_name}) closed",'yellow')

                    except Exception as e:
                        if item.retry < self._n_retry:
                            buffer = round((item.retry/self._n_retry),3)
                            await asyncio.sleep(buffer)
                            item = item._replace(retry=item.retry+1)
                            async with self._lock:  
                                await self._queue.put(item)
                            self._custom.warning.msg(item.name, f'retry({item.retry})',f"buff({buffer})")
                        else:
                            self._custom.error.msg(item.name,'drop', str(item.args))
                            if self._msg_traceback: traceback.print_exc()
                            # item.future.set_result(e) 
                            # raise e
                    finally:
                        tsp_finish = time.time() #! limiter
                        await self._wait_reset(tsp_start, tsp_finish)
                        self._queue.task_done()    

    # ------------------------------------------------------------------------ #
    #                                  server                                  #
    # ------------------------------------------------------------------------ #
    async def server(self):
        self._is_server_on = True
        while True:
            async with asyncio.TaskGroup() as tg:
                for i in range(self._n_worker):
                    tg.create_task(self.worker(),name=f"{self._name}-{i}")

    async def safe_restart(self):
        active = 0
        for _ in range(self._n_worker):
            await self._semaphore.acquire()
            active += 1
            print(active)
        
        async with self._lock:
            for _ in range(self._n_worker): await self._queue.put(None)
        self.xsession.restart()

        for _ in range(self._n_worker):
            self._semaphore.release()
            active -= 1
            print(active)

    # ------------------------------------------------------------------------ #
    #                                   other                                  #
    # ------------------------------------------------------------------------ #

    def _assert_produce(self,args, name):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")

        if not self._is_server_on:
            print(f"\033[31m balancer.server for {name}() is not running [{self._name}] \033[0m")

    async def _wait_reset(self, tsp_start:float, tsp_finish):
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)
        
        if self._msg_debug: self._custom.info.msg('finish',TimeFormat.timestamp(tsp_finish,'hmsf'),frame='',aligns=("<","^"), paddings=("","-")) 

        if seconds > 0.0:
            await asyncio.sleep(seconds)

        if self._msg_debug: 
            tsp_limit = time.time()            
            self._custom.info.msg('limit',TimeFormat.timestamp(tsp_limit,'hmsf'),frame='',aligns=("<",">"), paddings=("","-")) 

if __name__ =="__main__":

    import httpx
    balancer = Balancer()
    balancer.set_config(3,1,'outflow',3,msg_debug=True,msg_wrapper=True)
    balancer.set_xsession(xconnector = httpx.AsyncClient, close_method='aclose', close_status='is_closed')

    # @balancer.wrapper_xthrow
    @balancer.wrapper_xfetch
    async def xget(xconn:httpx.AsyncClient):
        await asyncio.sleep(1)
        resp = await xconn.get('https://www.naver.com/')
        return resp
    
    async def test1():
        tasks = [
            asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
            # asyncio.create_task(xget()),
        ]
        await asyncio.gather(*tasks)    

    async def test2():
        await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())

    async def test3():
        await xget()
        print('return')
        # await xget()
        # await xget()
        # await xget()
        # await xget()
        # await xget()
        # await xget()
        # await xget()
        # await xget()
        # await xget()

    def callback_cancel_all(future):
        [task.cancel() for task in asyncio.all_tasks()]

    async def main():

        server = asyncio.create_task(balancer.server())
        # task = asyncio.create_task(test1())
        # task = asyncio.create_task(test2())
        task = asyncio.create_task(test3())

        await asyncio.gather(task,server)   
        # await task


    asyncio.run(main())