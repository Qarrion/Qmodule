import logging
from datetime import datetime
from typing import Literal
import asyncio
from Qlimiter.util import CustomLog


class CustomMsg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def _str_from_tsp(self, time):
        datetime_time = datetime.fromtimestamp(time)
        return datetime_time.strftime("%S.%f")[:-3]

    def stream(self, status, *args):
        header = f'/{status:<10} ::: '
        body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
        self.msg(header + body)

    def strm_initiate(self, max_calls, seconds):
        status = 'initiate'
        var01 = f'max_calls({max_calls})'
        var02 = f'seconds({seconds})'
        self.stream(status,var01,var02,"")

    def strm_semaphore_acquire(self, sema:asyncio.Semaphore, max_calls):
        status = 'semaphore+'
        method = f">s({sema._value}/{max_calls})"
        var01 = f"{method:<12}"
        self.stream(status,"","",var01)

    def strm_semaphore_release(self, sema:asyncio.Semaphore, max_calls):
        status = 'semaphore-'
        method = f"s({sema._value+1}/{max_calls})<"
        var01 = f"{method:>12}"
        self.stream(status,"","",var01)

    def strm_waitfor_expire(self, tsp_ref, seconds):
        status = 'throttle'
        var01 = f'ref({self._str_from_tsp(tsp_ref)})'
        var02 = f'sec({seconds:.3f})'
        self.stream(status, var01, var02,"")

    def strm_task_error(self,fname, args, kwargs):
        status = 'exception'
        var01 = f'func({fname})'
        var02 = f'args({args})'
        var03 = f'kwargs({kwargs})'
        self.stream(status, var01, var02, var03)

    def strm_workerpool(self,text):
        status = 'workerpool'
        self.stream(status,text,"","")

    def strm_worker(self, text):
        status = 'worker'
        self.stream(status,text,"","")        

    def strm_register(self, limit, name):
        status = 'register'
        self.stream(status,limit,name,"")

    def strm_enqueue(self, fname, args, kwargs):
        status = 'enqueue'
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{kwargs}"
        self.stream(status,var01,var02,var03)
    # -------------------------------- message ------------------------------- #

if __name__ == "__main__":
    from Qlogger import Logger

    log = Logger("test", 'level')
    log.info('test info msg')
    log.debug('test debug msg')

    msg = CustomMsg(log, 'thread')
    msg.info.stream("msg")
    msg.debug.stream("msg")

    msg = CustomMsg(None, 'thread')
    msg.debug.stream("msg")
 