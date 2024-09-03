import asyncio
import time
from Qlogger import Logger
from collections import namedtuple
from typing import Literal
from Qlimiter.utils.dtime_print import from_tsp
from Qlimiter.utils.custom_print import cprint
from Qlimiter.session import ApiSess, SqlSess
#**********************************************************************


Item = namedtuple('item', ['future', 'xdef', 'args', 'kwargs', 'retry'])
class Limiter:

    def __init__(self, name='limiter'):      
        self._logger = Logger(logname=name, clsname='Limiter',context='async')  
        self._session = None 

        self._lock = asyncio.Lock()
        self.set_config()
        
    def set_config(self,  n_worker=3, s_window=1, n_retry=3, raise_in_drop=True, msg_flow=False):
        self._n_worker= n_worker
        self._n_retry = n_retry
        self._s_window = s_window

        self._sema = asyncio.Semaphore(n_worker)
        self._queue = asyncio.Queue(n_worker)
        
        self._msg_flow = msg_flow
        self._raise_in_drop = raise_in_drop

    # ------------------------------------------------------------------------ #
    #                                  session                                 #
    # ------------------------------------------------------------------------ #

    def session_config(self, session:Literal['api','sql'], custom=None, msg=False):
        """custom (sql - pgsql)"""
        if session == 'api':
            self._session = ApiSess()
        elif session == 'sql':
            if custom is None:
                cprint("limiter.session_config('sql', msg=True) + custom = pgsql",'red')
                return 0
            self._session = SqlSess(pgsql=custom)

        if msg: self._logger.info.msg(self._session.pclass.__name__,debug_var='msg_session')

    async def session_x_reset(self):
        if self._session is not None : 
            for _ in range(self._n_worker):
                await self._sema.acquire()
                await self.rate_limit_entry('x_reset_entry')
                    
            await self._session.x_reset()
            self._logger.info.msg("RESET",f"{self._session.pclass.__name__}",widths=(1,2),paddings="=",aligns="^")

            for _ in range(self._n_worker):
                await self.rate_limit_exit('x_reset_exit')
                self._sema.release()

    async def session_x_start(self):
        await self._session.x_start()

    #**************************************************************************
    def __call__(self, xdef):
        async def wrapper(*args, **kwargs):
            retry = 0
            fname = xdef.__name__
            async with self._sema:
                while True:
                    await self.rate_limit_entry(fname)
                    try:
                        if self._session is not None:
                            result = await xdef(self._session.session, *args, **kwargs)
                        else:
                            result = await xdef(*args, **kwargs)
                        return result 

                    except Exception as e:
                        if (retry:= retry+1) <= self._n_retry:
                            sec = round(0.3*(retry/self._n_retry),3)
                            await asyncio.sleep(sec)
                            self._logger.warning.msg(f'except [{sec:.2f}s]',f'retry({retry})',
                                                    e.__class__.__name__, fname=fname)
                        else:
                            self._logger.error.msg(f'except [Error]',f'drop',
                                    f"raise_on_drop({self._raise_in_drop})", fname=fname)
                            if self._raise_in_drop:
                                raise e
                            else:
                                return None
                    finally:
                        await self.rate_limit_exit(fname)
        return wrapper
    #**************************************************************************
    # ------------------------------------------------------------------------ #
    #                                  limiter                                 #
    # ------------------------------------------------------------------------ #
    async def rate_limit_exit(self, fname='limit_exit'):
        # ---------------------- only_for_last_queue --------------------- #
        loop = asyncio.get_running_loop()
        loop_time_expire = loop.time() + 1.0
        await self._queue.put(loop_time_expire)
        self.msg_logger('reach',fname)
        
    async def rate_limit_entry(self, fname='limit_entry'):
        async with self._lock:
            n_worker = self._n_worker - self._sema._value
            while n_worker + self._queue.qsize() > self._n_worker: # Ensure that the queue is not empty
                loop_time_expire = await self._queue.get()
                loop = asyncio.get_running_loop()
                curr = loop.time()
                await asyncio.sleep(loop_time_expire-curr)
                self.msg_logger('limit',fname=fname, sleep=loop_time_expire-curr)

                self._queue.task_done()         
        self.msg_logger('start',fname)

    # ------------------------------------------------------------------------ #
    #                                  logging                                 #
    # ------------------------------------------------------------------------ #
    def msg_logger(self, msg_type:Literal['start','limit','reach'], fname:str, sleep=0.0):
        if self._msg_flow:
            sema = self._n_worker - self._sema._value
            nque = self._queue.qsize()
            if msg_type == 'start':
                self._logger.info.msg(f'start   W({sema}) R({nque})',
                from_tsp(time.time(),'hmsf'), fname=fname, aligns=("<","<"), paddings=("","-"), debug_var='msg_flow')
                    
            elif msg_type == 'limit':
                self._logger.info.msg(f'[{sleep:.2f}s] W({sema}) R({nque+1}->{nque})',
                from_tsp(time.time(),'hmsf'), fname=fname, aligns=("<","^"), paddings=("","-"), debug_var='msg_flow')
            
            elif msg_type == 'reach':
                self._logger.info.msg(f'reach   W({sema}) R({nque-1}->{nque})',
                from_tsp(time.time(),'hmsf'), fname=fname, aligns=("<",">"), paddings=("","-"), debug_var='msg_flow')

if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                  session                                 #
    # ------------------------------------------------------------------------ #
    import httpx
    limiter = Limiter()
    limiter.set_config(3,1,3,msg_flow=True)
    limiter.session_config(session='api')

    @limiter
    async def xget(xclient:httpx.AsyncClient, market='KRW-BTC'):
        url_candle='https://api.upbit.com/v1/candles/minutes/1'
        headers = {"Accept": "application/json"}
        max_count = 200
        params=dict(market = 'KRW-BTC', count = 200, to = None)
        resp = await xclient.get(url=url_candle, headers=headers, params=params)
        return resp

    @limiter
    async def xget_e(xclient:httpx.AsyncClient, market='KRW-BTC'):
        url_candle='https://api.upbit.com/v1/candlesx/minutes/1e'
        headers = {"Accept": "application/json"}
        max_count = 200
        params=dict(market = 'KRW-BTC', count = 200, to = None)
        resp = await xclient.get(url=url_candle, headers=headers, params=params)
        # print(resp)
        resp.raise_for_status()
        return resp
        
    async def task_0():
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')

    async def task_1():
        tasks=[
            asyncio.create_task(xget(market='KRW-BTC'),name='t1'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t2'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t3'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t4'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t5'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t6'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t7'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t8'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t9'),
            asyncio.create_task(xget(market='KRW-BTC'),name='t0'),
        ]
        await asyncio.gather(*tasks)

    async def task_e():
        tasks=[
            asyncio.create_task(xget_e(market='KRW-BTC')),
            asyncio.create_task(xget_e(market='KRW-BTC')),
            asyncio.create_task(xget_e(market='KRW-BTC')),
        ]
        await asyncio.gather(*tasks)

    async def main():
        await limiter.session_x_start()
        asyncio.current_task().set_name('main')
        # asyncio.create_task(limiter.manager())

        # print(resp.json())
        # await xget()
        # await task_0()
        # await limiter.session_x_reset()
        # await task_0()
        await task_0()
        
        # await task_1()
        
    asyncio.run(main())