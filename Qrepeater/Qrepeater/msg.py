import logging
from typing import Literal
from Qrepeater.utils.customlog import CustomLog
import inspect
from datetime import datetime

class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def stream(self, status, *args):
        # frame = f'{inspect.stack()[2].function}.{status}'
        frame = f'{inspect.currentframe().f_back.f_code.co_name}.{status}'
        header = f'{frame:<20} ::: '
        body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
        self.msg(header + body) 

    def strm_timer_wait(self, datetime_next, timedelta_ms):
        status=''
        str_nxt = datetime_next.strftime("%M:%S.%f")[:-3]

        sec_rem = timedelta_ms.total_seconds()
        dtm_rem = datetime.fromtimestamp(sec_rem)
        str_lft = dtm_rem.strftime("%M:%S.%f")[:-3]

        var3 = ''
        self.stream(status, str_nxt, str_lft, var3)

    def strm_async_timeout(self, fname, args, timeout):
        var01 = fname
        var02 = f"{args}"
        var03 = timeout
        self.stream('', var01, var02, var03)

    def strm_thread_alldone(self):
        self.stream('all done!','','','')

if __name__ =="__main__":
    from Qlogger import Logger
    logger = Logger('test','level')
    
    msg = Msg(logger, 'async')
    msg.info.strm_async_timeout('dd',(2,3),3)