import asyncio
import logging
from typing import Literal, Callable

from Qconsume.tools.taskq import Taskq
import time



class Consume(Taskq):

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)
        self._custom.info.msg('Limiter')

        self._limit:str = None
        self._max_worker:int = None
        self._seconds:int = None

        self._semaphore:asyncio.Semaphore = None

    def limiter(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow']):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit = limit

        self._semaphore = asyncio.Semaphore(max_worker)
        # self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})",f"timeout({timeout})")
        self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})")
    
    # ------------------------------------------------------------------------ #
    #                                overriding                                #
    # ------------------------------------------------------------------------ #
    def register(self, async_def: Callable, fname: str = None):
        if fname is None : fname = async_def.__name__ 
        self._registry[fname] = self._wrapper_throttle(async_def)
        self._custom.info.msg('', fname, task=False)


    @property
    def queue(self):
        return self.queue
    
    async def consumer(self):
        while True:
            item = await self.enqueue()
            await self.execute(item)
            
    def _wrapper_throttle(self, async_def:Callable):
        async def wrapper(*args):
            propagate_exception = None
            # msg_arg = (async_def.__name__, self._semaphore, self._max_worker)
            async with self._semaphore:
                # self.msg.debug.semaphore("acquire", *msg_arg) 
                self._msg_semaphore('acquire',async_def.__name__)
                # ------------------------------------------------------------ #
                try: 
                    tsp_start = time.time()     
                    result = await async_def(*args)

                except Exception as e:
                    # self.msg.error.exception('job',async_def.__name__, args)
                    self._custom.error.msg('job',async_def.__name__,str(args))
                    propagate_exception = e
                # ------------------------------------------------------------ #
                finally:
                    tsp_finish = time.time()
                    await self._wait_reset(tsp_start, tsp_finish)
                    # self.msg.debug.semaphore("release", *msg_arg) 
                    self._msg_semaphore('release',async_def.__name__)
                    #? propagate exception to retry
                    if propagate_exception:
                        raise propagate_exception
        return wrapper
    
    async def _wait_reset(self, tsp_start:float, tsp_finish):
        #! TODO msg replace with methods _msg_xxx
        if self._limit == 'inflow':
            tsp_ref = tsp_start
        elif self._limit == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            #?  tsp_ref 여기 출력 양식 변경
            self._custom.debug.msg(self._limit, tsp_ref, seconds,frame='wait',task=True)
            await asyncio.sleep(seconds)
        else:
            self._custom.debug.msg(self._limit, tsp_ref, 0,frame='wait',task=True)
    # ------------------------------------------------------------------------ #
    #                                  dev_msg                                 #
    # ------------------------------------------------------------------------ #
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f">s({self._semaphore._value}/{self._max_worker})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({self._semaphore._value+1}/{self._max_worker})<"
            var01 = f">{queue:>11}"
        self._custom.debug.msg(context,fname,var01,frame='sema',task=True)

if __name__ == "__main__":
    from Qconsume .utils .logger_color import ColorLog

    logger = ColorLog('limiter','blue')
    
    cons = Consume(logger)
    cons.limiter(5, 1, 'inflow')

    log_func = ColorLog('work', 'yellow')
    async def myfun(a,b,c):
        log_func.info('start')
        await asyncio.sleep(3)
        log_func.info('end')

    cons.register(myfun)

    async def put():
        await cons.enqueue('myfun',(1,2,3))
        await cons.enqueue('myfun',(2,3,4))

    async def run():
        item = await cons.dequeue()
        await cons.execute(item)

    async def main():
        await put()
        await run()

    asyncio.run(main())
    