from Qlimiter.util.log_custom import CustomLog
from datetime import datetime
from typing import Literal
import logging
import asyncio
import inspect



class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def test(self, test):
        self.text('test',test)

    def initiate(self, max_calls, seconds):
        #Limiter
        var01 = f'max_calls({max_calls})'
        var02 = f'seconds({seconds})'

        self.args('limiter',var01,var02)

    def register(self, limit_type, name):
        #Job
        self.args(limit_type,name)

    def enqueue(self, fname, args, retry):
        #job
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"{retry}"
        self.args('function',var01,var02,var03,task_name=True)

    def dequeue(self, fname, args, retry):
        #Job
        var01 = f"{fname}"
        var02 = f"{args}"
        var03 = f"retry({retry})"
        self.args('execute',var01,var02,var03,task_name=True)

    def semaphore(self, context:Literal['acquire','release'], fname, sema:asyncio.Semaphore, max_calls):
        #job
        status = context
        if context=="acquire":
            queue = f">s({sema._value}/{max_calls})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({sema._value+1}/{max_calls})<"
            var01 = f">{queue:>11}"
        self.args(status,fname,"",var01,task_name=True)

    def wait_reset(self, tsp_ref, seconds,limit):
        #Job
        status = limit
        var01 = f'sec({seconds:.3f})'
        var02 = f'ref({self._str_from_tsp(tsp_ref)})'
        self.args(status, var01, var02, "",task_name=True)

    def exception(self, status, fname, args, retry):
        #Job
        var01 = f'{fname}'
        var02 = f'{args}'
        var03 = f'{retry}'
        self.args(status, var01, var02, var03, task_name=True)

    def _str_from_tsp(self, time):
        datetime_time = datetime.fromtimestamp(time)
        return datetime_time.strftime("%S.%f")[:-3]
    
# if __name__ == "__main__":
#     from Qlogger import Logger

#     log = Logger("test", 'level')
#     log.info('test info msg')
#     log.debug('test debug msg')

#     msg = Msg(log, 'thread')
#     msg.error.test("msg")
#     # msg.debug.stream("msg")

    # msg = Msg(None, 'thread')
    # msg.debug.stream("msg")
 