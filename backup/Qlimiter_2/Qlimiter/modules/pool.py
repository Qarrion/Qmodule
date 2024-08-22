import asyncio
from collections import namedtuple
from re import T
import time
import traceback
from typing import Callable, Literal
from Qlimiter.utils.logger_custom import CustomLog
from Qlimiter.modules.session import Session
from Qlimiter.utils.print_color import cprint
from Qlimiter.utils.format_time import TimeFormat

item_xfetch = namedtuple('item_xfetch', ['future', 'name', 'args', 'kwargs', 'retry'])
item_xthrow = namedtuple('item_xthrow', ['name', 'args', 'kwargs', 'retry'])

class Pool:

    def __init__(self, name:str='Pool', msg=True):
        """
        >>> # 
        balancer = Balancer()
        balancer.set_config()
        balancer.set_xsession()
        """
        # -------------------------------------------------------------------- #
        CLSNAME = 'Pool'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = CustomLog.getlogger(name=name)
            print(f"\033[31m No Module Qlogger \033[0m")
        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        # -------------------------------------------------------------------- #
        # self.xsession = None
        self._session = None
        self._xdefs:dict = dict()

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

    def set_session(self, session:Session):
        """self.xconn = connect()"""
        self._session = session()
        self._custom.info.msg(self._session.pclass.__name__)
    # ------------------------------------------------------------------------ #
    #                                  wrapper                                 #
    # ------------------------------------------------------------------------ #
    def wait_for_result(self, xdef):      
        if self._msg_wrapper : self._custom.info.msg(f"{xdef.__name__}")
        self._set_xdef(xdef)

        async def wrapper(*args, **kwargs):
            return await self._xfetch(xdef, args, kwargs)
            
        return wrapper

    def fire_and_forget(self, xdef):      
        if self._msg_wrapper : self._custom.info.msg(f"{xdef.__name__}")
        self._set_xdef(xdef)
        async def wrapper(*args, **kwargs):
            return await self._xthrow(xdef, args, kwargs)
        return wrapper
    
    # -------------------------------- private ------------------------------- #
    def _set_xdef(self,xdef):
        self._xdefs[xdef.__name__] = xdef
        return xdef
    
    async def _xfetch(self, xdef, args=(), kwargs:dict=None):
        name = xdef.__name__
        self._assert_produce(args=args,name=name)
        future = asyncio.Future()
        retry = 0

        item = item_xfetch(future=future,name=name,args=args,kwargs=kwargs,retry=retry)
        async with self._lock:
            await self._queue.put(item)

        result = await future
        return result
    
    async def _xthrow(self, xdef, args=(), kwargs:dict=None):
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
    async def _worker(self, msg_close=False):
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

                        # if self.xsession is not None:
                        if self._session is not None:
                            # result = await asyncio.wait_for(self.xdefs[item.name](self.xsession.xconn, *item.args, **kwargs),50)
                            result = await asyncio.wait_for(self._xdefs[item.name](self._session.session, *item.args, **kwargs),50)
                        else:
                            result = await asyncio.wait_for(self._xdefs[item.name](*item.args, **kwargs),50)

                        if item.__class__.__name__ == "item_xfetch":
                            item.future.set_result(result)  
                        
                    except asyncio.exceptions.CancelledError as e:
                        cprint(f" - worker ({task_name}) closed",'yellow')
                        await asyncio.sleep(2)  # Graceful cleanup (example)
                        raise 
                    except Exception as e:
                        if item.retry < self._n_retry:
                            item = item._replace(retry=item.retry+1)
                            buffer = round((item.retry/self._n_retry),3)
                            # buffer = 0.1 * //(item.retry+1)
                            await asyncio.sleep(buffer)
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
        # await self.xsession.start()
        self._is_server_on = True
        await self._session.restart() 
        try:
            while True:
                    async with asyncio.TaskGroup() as tg:
                        for i in range(self._n_worker):
                            tg.create_task(self._worker(),name=f"{self._name}-{i}")
        except asyncio.CancelledError:
            task_name = asyncio.current_task().get_name()
            cprint(f" - worker ({task_name}) closed",'yellow')

    async def safe_restart(self):
        async with self._lock:
            for _ in range(self._n_worker):
                await self._semaphore.acquire()
            
            # async with self._lock:
            for _ in range(self._n_worker): await self._queue.put(None)
            # self.xsession.restart()
            await self._session.restart()
            self._custom.info.msg("restart",widths=3,aligns="^",paddings='-')

            for _ in range(self._n_worker):
                self._semaphore.release()


    # ------------------------------------------------------------------------ #
    #                                   other                                  #
    # ------------------------------------------------------------------------ #

    def _assert_produce(self,args, name):
        if not isinstance(args,tuple): 
            print(f"\033[31m args is not tuple \033[0m")

        if not self._is_server_on:
            print(f"\033[31m pool.server for {name}() is not running [{self._name}] \033[0m")

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
    balancer = Pool()
    balancer.set_config(3,1,'outflow',3,msg_debug=True,msg_wrapper=True)
    # balancer.set_xsession(xconnector = httpx.AsyncClient, close_method='aclose', close_status='is_closed')

    # from Qlimiter.modules.session import Session


    class ApiSess(Session):
        pclass = httpx.AsyncClient
        async def restart(self):
            if self.session is None:
                self.session = httpx.AsyncClient()
            else: 
                await self.session.aclose()
                self.session = httpx.AsyncClient()


    balancer.set_session(session=ApiSess)
        

    # @balancer.fire_and_forget
    @balancer.wait_for_result
    async def xget(xconn:httpx.AsyncClient):
        # await asyncio.sleep(1)
        resp = await xconn.get('https://www.naver.com/')
        cprint('done',color='green')
        return resp
    
    # @balancer.fire_and_forget
    @balancer.wait_for_result
    async def xget_er(xconn:httpx.AsyncClient):
        # await asyncio.sleep(1)
        resp = await xconn.get('https://www.naver.com2/')
        return resp
    
    async def task0():
        await xget()#1
        await xget()#2
        await xget_er()#3
        await xget()#4
        await xget()#5
        await xget()#6
        await xget()#7
        await xget()#8

    async def task1():
        tasks = [
            asyncio.create_task(xget()),#1
            asyncio.create_task(xget()),#2
            asyncio.create_task(xget_er()),#3
            asyncio.create_task(xget()),#4
            asyncio.create_task(xget()),#5
            asyncio.create_task(xget()),#6
            asyncio.create_task(xget()),#7
            asyncio.create_task(xget()),#8
        ]
        await asyncio.gather(*tasks)    

    async def task2():
        await asyncio.create_task(xget())
        await asyncio.create_task(xget())
        await asyncio.create_task(xget())
        await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())
        # await asyncio.create_task(xget())

    async def task3():
        await xget()
        await xget()
        await xget()
        await xget()
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
        task = await task1()
        # task = asyncio.create_task(test1())
        # task = asyncio.create_task(test2())
        # task = asyncio.create_task(test3())

        await asyncio.gather(task,server)   
        # await task


    asyncio.run(main())