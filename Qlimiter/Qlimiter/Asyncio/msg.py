# from Qlimiter.util import CustomLog
from Qlimiter.util.log_custom import CustomLog
from datetime import datetime
from typing import Literal
import logging
import asyncio
import inspect


class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def initiate(self, max_calls, seconds):
        #Limiter
        var01 = f'max_calls({max_calls})'
        var02 = f'seconds({seconds})'
        self.args('limiter',var01,var02)

    def register(self, limit_type, name):
        #Job
        self.args(limit_type,name)

    def enqueue(self, fname, args, kwargs):
        #job
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{kwargs}"
        self.args('function',var01,var02,var03)

    def handler(self, fname, args, kwargs):
        #Job
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{kwargs}"
        self.args('execute',var01,var02,var03)

    def semaphore(self, context:Literal['acquire','release'], fname, sema:asyncio.Semaphore, max_calls):
        #job
        status = context
        if context=="acquire":
            queue = f">s({sema._value}/{max_calls})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({sema._value+1}/{max_calls})<"
            var01 = f">{queue:>11}"
        self.args(status,fname,"",var01)

    def wait_reset(self, tsp_ref, seconds,limit):
        #Job
        status = limit
        var02 = f'ref({self._str_from_tsp(tsp_ref)})'
        var01 = f'sec({seconds:.3f})'
        self.args(status, var01, var02, "")

    def exception(self, status, fname, args, kwargs):
        #Job
        var01 = f'{fname}'
        var02 = f'{args}'
        var03 = f'{kwargs}'
        self.args(status, var01, var02, var03)

    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #

    def _str_from_tsp(self, time):
        datetime_time = datetime.fromtimestamp(time)
        return datetime_time.strftime("%S.%f")[:-3]
    
    # ------------------------------------------------------------------------ #
    #                            base stream formma                            #

    # ------------------------------------------------------------------------ #
    # def stream(self, status, *args):
    #     frame = f'{inspect.stack()[2].function}.{status}'
    #     header = f'/{frame:<20} ::: '
    #     body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
    #     self.msg(header + body)

    # ------------------------------------------------------------------------ #




# ---------------------------------------------------------------------------- #
    def strm_workerpool(self,text):
        status = 'workerpool'
        self.stream(status,text,"","")

    def strm_worker(self, text):
        status = 'worker'
        self.text(status,text)        


    # -------------------------------- message ------------------------------- #

if __name__ == "__main__":
    from Qlogger import Logger

    log = Logger("test", 'level')
    log.info('test info msg')
    log.debug('test debug msg')

    msg = Msg(log, 'thread')
    msg.info.stream("msg")
    msg.debug.stream("msg")

    msg = Msg(None, 'thread')
    msg.debug.stream("msg")
 