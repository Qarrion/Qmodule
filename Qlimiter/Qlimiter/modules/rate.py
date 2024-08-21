# -------------------------------- ver 240511 -------------------------------- #
# tools
# -------------------------------- ver 240527 -------------------------------- #
# limiter return
# -------------------------------- ver 240607 -------------------------------- #
# xdef hint remove
# -------------------------------- ver 240609 -------------------------------- #
# kwargs limit=True

from Qlimiter.utils.logger_custom import CustomLog
from Qlimiter.utils.format_time import TimeFormat
from typing import Callable, Literal

from functools import wraps
import asyncio, time, traceback

# from Qlimiter.modules.session import Xsession


class Rate:
    def __init__(self, name:str='limiter', msg=True):
        """ 
        >>> # named singleton
        limiter = Limiter('limiter')
        limiter.set_rate(3, 1, 'outflow')
        xldef = limiter.wrapper(xdef,traceback=False,msg=True)
        xldef(limit=False)
        >>> # case
        limiter = Limiter('g_mkt')._set(5,1,'outflow')
        """
        CLSNAME = 'Limiter'
        try:
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = CustomLog.getlogger(name=name)

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        self.xsession = None

    def set_config(self, n_worker:int, seconds:float, limit:Literal['inflow','outflow','midflow'],
        msg_traceback=False, msg_debug=False):
        
        self._n_worker = n_worker
        self._seconds = seconds
        self._limit_type = limit

        self._msg_traceback = msg_traceback
        self._msg_debug = msg_debug

        self._semaphore = asyncio.Semaphore(n_worker)
        self._custom.info.msg(limit,f"max({n_worker})",f"sec({seconds})" )

    # def set_xsession(self, xconnector:Callable, close_method:str, close_status:str):
    #     """>>> # used case 
    #     set_xsession(xconnector = httpx.AsyncClient, close_method='aclose', close_status='is_closed')
    #     set_xsession(xconnector = pgsql.xconnect_pool, close_method='close', close_status='closed')"""
    #     self.xsession = Xsession(xconnector, close_method, close_status) 
    #     self.xsession.start()

    def limiter(self, xdef):
        @wraps(xdef)
        async def wrapper(*args, limit=True, **kwargs):
            if limit:
                async with self._semaphore:
                    try: 
                        tsp_start = time.time()     
                        if self._msg_debug: 
                            self._custom.info.msg('start',TimeFormat.timestamp(tsp_start,'hmsf'),frame='',aligns=("<","<"), paddings=("","-")) 

                        # if self.xsession:
                        #     result = await xdef(self.xsession.xconn, *args, **kwargs)
                        # else:
                        result = await xdef(*args, **kwargs)
                        return result
                    
                    except asyncio.exceptions.CancelledError as e:
                        task_name = asyncio.current_task().get_name()
                        print(f"\033[33m Interrupted ! limiter ({task_name}) \033[0m")

                    except Exception as e:
                        self._custom.error.msg(xdef.__name__,'except',e.__class__.__name__ )
                        if self._msg_traceback: traceback.print_exc()
                        raise e
                        
                    finally:
                        tsp_finish = time.time()
                        await self.wait_reset(tsp_start, tsp_finish)
            else:
                result = await xdef(*args, **kwargs)
                return result
        return wrapper
    
    async def wait_reset(self, tsp_start:float, tsp_finish):
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

    # async def safe_reset(self):
    #     await asyncio.sleep(0.2)
    #     active = 0
    #     for _ in range(self._n_worker):
    #         await self._semaphore.acquire()
    #         active += 1
    #         print(active)

    #     await asyncio.sleep(1)
    #     print('do someThing')

    #     for _ in range(self._n_worker):
    #         self._semaphore.release()
    #         active -= 1
    #         print(active)


#TODO  httpx 와 asyncpool을 이용해서 안전하게 restart 까지
# async def safe(self): 활용
# https://www.psycopg.org/psycopg3/docs/advanced/pool.html#connection-pools
# https://www.psycopg.org/psycopg3/docs/advanced/async.html
# httpx는 내부적으로 풀이용 
# psycopg 는 connection-pools 써야 
# restart에 신경쓰고
# fetch는 limiter
# balancer는 throw에 쓸까함

if __name__ =="__main__":

    import httpx
    rate = Rate()
    rate.set_config(3, 1, 'outflow', msg_debug=True)
    # limiter.set_xsession(xconnector = httpx.AsyncClient, close_method='aclose', close_status='is_closed')
    # limiter.set_xconn(xconn=Xclient)

    @rate.limiter
    async def xget(xconn:httpx.AsyncClient):
        resp = await xconn.get('https://www.naver.com/')
        # print(resp)

    async def test1():
        async with httpx.AsyncClient() as xconn:
            tasks = [
                asyncio.create_task(xget(xconn)),#1 
                asyncio.create_task(xget(xconn)),#2
                asyncio.create_task(xget(xconn)),#3
                asyncio.create_task(xget(xconn)),#4
                # asyncio.create_task(xget(xconn)),#5
                # asyncio.create_task(xget(xconn)),#6
                # asyncio.create_task(xget(xconn)),#7
                # asyncio.create_task(xget(xconn)),#8
                # asyncio.create_task(xget(xconn)),#9
                # asyncio.create_task(xget(xconn)),#0
            ]
            await asyncio.gather(*tasks)

    async def test2():
        async with httpx.AsyncClient() as xconn:
            await asyncio.create_task(xget(xconn))#1
            await asyncio.create_task(xget(xconn))#2
            await asyncio.create_task(xget(xconn))#3
            await asyncio.create_task(xget(xconn))#4
            # await asyncio.create_task(xget(xconn))#5
            # await asyncio.create_task(xget(xconn))#6
            # await asyncio.create_task(xget(xconn))#7
            # await asyncio.create_task(xget(xconn))#8
            # await asyncio.create_task(xget(xconn))#9
            # await asyncio.create_task(xget(xconn))#0

    async def test3():
        async with httpx.AsyncClient() as xconn:
            await xget(xconn)#1
            await xget(xconn)#2
            await xget(xconn)#3
            await xget(xconn)#4
            await xget(xconn)#5
            await xget(xconn)#6
            await xget(xconn)#7
            await xget(xconn)#8
            await xget(xconn)#9
            await xget(xconn)#0

    async def main():
        # task1 = asyncio.create_task(test1())
        # await task1
        # await test1()
        await test2()
        # await test3()

    asyncio.run(main())

    

    # async def main():
    #     tasks = [
    #         asyncio.create_task(loop()),
    #         asyncio.create_task(limiter.safe_reset())
    #     ]
    #     await asyncio.gather(* tasks)








    # ----------------------------- error control ---------------------------- #
    # @limiter.wrapper
    # async def xfunc(x):
    #     print(f'start {x}')
    #     await asyncio.sleep(0.5)
    #     print(f'finish {x}')
    # @limiter.wrapper
    # async def xerror(x):
    #     print(f'start {x}')
    #     await asyncio.sleep(0.5)
    #     raise ValueError
    #     print(f'finish {x}')


    # async def main():
    #     tasks = [
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1,limit=False)),
    #         asyncio.create_task(xfunc(1)),
    #         asyncio.create_task(xerror(1)),
    #         asyncio.create_task(xfunc(1)),
    #         asyncio.create_task(xfunc(1)),
    #     ]
    #     await asyncio.gather(*tasks)

    # asyncio.run(main())



