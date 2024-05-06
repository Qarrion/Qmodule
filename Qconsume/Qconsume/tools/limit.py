import time
from Qconsume.utils.logger_custom import CustomLog

from typing import Callable, Literal
import asyncio, logging, traceback




class Limit:

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')

    def set_rate(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow']):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})")

    def _wrapper_throttle(self, async_def:Callable):
        async def wrapper(*args):
            propagate_exception = None

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
    
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f">s({self._semaphore._value}/{self._max_worker})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({self._semaphore._value+1}/{self._max_worker})<"
            var01 = f">{queue:>11}"
        self._custom.debug.msg(context,fname,var01,frame='sema',task=True)

    async def _wait_reset(self, tsp_start:float, tsp_finish):
        #! TODO msg replace with methods _msg_xxx
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        if seconds > 0:
            #?  tsp_ref 여기 출력 양식 변경
            self._custom.debug.msg(self._limit_type, tsp_ref, seconds,frame='wait',task=True)
            await asyncio.sleep(seconds)
        else:
            self._custom.debug.msg(self._limit_type, tsp_ref, 0,frame='wait',task=True)

    