import asyncio, time
from collections import namedtuple
from typing import Literal
from Qtask.modules._session import ApiSess, SqlSess
from Qtask.utils.dtime_print import from_tsp
from Qtask.utils.custom_print import cprint
from Qlogger import Logger
import traceback
Item = namedtuple('item', ['future', 'xdef', 'args', 'kwargs', 'retry'])

class Limiter:
    def __init__(self, name='limiter'):      
        self._logger = Logger(logname=name, clsname='Limiter',context='async')  
        self._session = None 

        self._lock = asyncio.Lock()
        self.set_config()
        
    def set_config(self,  n_worker=3, s_window=1.0, n_retry=3, raise_in_drop=True, traceback_in_warn = True, msg_flow=False):
        self._n_worker= n_worker
        self._s_window = s_window
        self._n_retry = n_retry

        self._sema = asyncio.Semaphore(n_worker)
        self._queue = asyncio.Queue(n_worker)
        
        self._msg_flow = msg_flow
        self._raise_in_drop = raise_in_drop
        self._traceback_in_warn = traceback_in_warn
        
    # ------------------------------------------------------------------------ #
    #                                  session                                 #
    # ------------------------------------------------------------------------ #
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
    # ------------------------------------------------------------------------ #
    async def session_reset(self):
        if self._session is not None : 
            for _ in range(self._n_worker):
                await self._sema.acquire()
                await self._limit_entry('x_reset_entry')
                    
            await self._session.x_reset()
            self._logger.info.msg("RESET",f"{self._session.pclass.__name__}",widths=(1,2),paddings="=",aligns="^")

            for _ in range(self._n_worker):
                await self._limit_exit('x_reset_exit')
                self._sema.release()
    # ------------------------------------------------------------------------ #
    async def session_start(self):
        await self._session.x_start()
        
    # ------------------------------------------------------------------------ #
    #                                  wrapper                                 #
    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #
    async def _limit_exit(self, fname='limit_exit'):
        # ---------------------- only_for_last_queue --------------------- #
        time_expire = asyncio.get_running_loop().time() + self._s_window
        await self._queue.put(time_expire)
        self.__msg_logger('reach',fname)
    # ------------------------------------------------------------------------ #
    async def _limit_entry(self, fname='limit_entry'):
        async with self._lock:
            n_worker = self._n_worker - self._sema._value
            while n_worker + self._queue.qsize() > self._n_worker: # Ensure that the queue is not empty
                time_expire = await self._queue.get()
                curr = asyncio.get_running_loop().time()
                self.__msg_logger('limit',fname=fname, sleep=time_expire-curr) 
                await asyncio.sleep(time_expire-curr)
                self._queue.task_done()         
            self.__msg_logger('start',fname)
    # ------------------------------------------------------------------------ #
    async def _backoff(self, retry):
        sec = round(0.3*(retry/self._n_retry),3)
        await asyncio.sleep(sec)
    # ------------------------------------------------------------------------ #
    def __call__(self, xdef):
        async def wrapper(*args, **kwds):
            retry=0
            async with self._sema:
                while True:
                    await self._limit_entry()
                    try:
                        if self._session is not None:
                            if self._session.session is None: await self.session_start()
                            result = await xdef(self._session.session, *args, **kwds)
                        else:
                            result = await xdef(*args, **kwds)
                        return result
                    except Exception as e:
                        if retry < self._n_retry:
                            retry += 1
                            await self._backoff(retry)
                            self.__msg_retry(xdef.__name__,args,retry)
                            if self._traceback_in_warn: traceback.print_exc()
                            # if self._traceback_in_warn: raise e
                        else:
                            self.__msg_drop(xdef.__name__,args)
                            if self._raise_in_drop: raise e
                    finally:
                        await self._limit_exit()
        return wrapper
        
    # ------------------------------------------------------------------------ #
    #                                  logging                                 #
    # ------------------------------------------------------------------------ #
    def __msg_logger(self, msg_type:Literal['start','limit','reach'], fname:str, sleep=0.0):
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
    
    def __msg_retry(self,fname,args,retry):
        if self._logger is not None:
            self._logger.warning.msg(
                f'except{str(args)}',f'retry({retry})',fname=fname)
            
    def __msg_drop(self,fname,args):
        if self._logger is not None:
            self._logger.error.msg(
                f'except{str(args)}',f'drop',fname=fname)               

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
    
    async def task_0():
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')
        resp = await xget(market='KRW-BTC')
        
    async def main():
        await limiter.session_start()
        asyncio.current_task().set_name('main')
        await task_0()
        
    asyncio.run(main())