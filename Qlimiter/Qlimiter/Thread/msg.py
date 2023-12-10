import logging
from datetime import datetime
from typing import Literal
import threading
from Qlimiter.util import CustomLog
import inspect

class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def _str_from_tsp(self, time):
        datetime_time = datetime.fromtimestamp(time)
        return datetime_time.strftime("%S.%f")[:-3]
    
    # ------------------------------------------------------------------------ #
    #                            base stream formma                            #
    # ------------------------------------------------------------------------ #
    def stream(self, status, *args):
        frame = f'{inspect.stack()[2].function}.{status}'
        header = f'/{frame:<20} ::: '
        body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
        self.msg(header + body)

    # ------------------------------------------------------------------------ #
    def strm_initiate(self, max_calls, seconds):
        status = ''
        var01 = f'max_calls({max_calls})'
        var02 = f'seconds({seconds})'
        self.stream(status,var01,var02,"")

    def strm_register(self, limit, name):
        self.stream(limit,name,"","")

    def strm_enqueue(self, fname, args, kwargs):
        status = ''
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{kwargs}"
        self.stream(status,var01,var02,var03)
        
    def strm_handler(self, fname, args, kwargs):
        status = ''
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{kwargs}"
        self.stream(status,var01,var02,var03)

    def strm_semaphore(self, context:Literal['acquire','release'], fname, sema:threading.Semaphore, max_calls):
        if context=="acquire":
            status = 'semaphore+'
            queue = f">s({sema._value}/{max_calls})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            status = 'semaphore-'
            queue = f"s({sema._value+1}/{max_calls})<"
            var01 = f">{queue:>11}"
        self.stream(status,fname,"",var01)

    def strm_wait_expire(self, tsp_ref, seconds,limit):
        status = limit
        var02 = f'ref({self._str_from_tsp(tsp_ref)})'
        var01 = f'sec({seconds:.3f})'
        self.stream(status, var01, var02, "")

    def strm_job_error(self,fname, args, kwargs):
        status = 'exception#'
        var01 = f'{fname}'
        var02 = f'{args}'
        var03 = f'{kwargs}'
        self.stream(status, var01, var02, var03)

    def strm_workerpool(self):
        status = 'start'
        self.stream(status,"","","")

    def strm_worker(self):
        status = 'start'
        self.stream(status,"","","")        
    # ------------------------------------------------------------------------ #

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
 