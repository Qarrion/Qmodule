import logging
from typing import Literal
from Qrepeater.utils.log_custom import CustomLog
from datetime import datetime

class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def timer(self, datetime_next, timedelta_ms):
        status='wait'
        str_nxt = datetime_next.strftime("%M:%S.%f")[:-3]

        sec_rem = timedelta_ms.total_seconds()
        dtm_rem = datetime.fromtimestamp(sec_rem)
        str_lft = dtm_rem.strftime("%M:%S.%f")[:-3]

        var3 = ''
        self.args(status, str_nxt, str_lft, var3,task_name=True)

    def job(self, status, fname):
        self.text(status,fname,task_name=True)
    # def catch(self, e):
    #     self.text(type(e).__name__, str(e))

    def exception(self, fname, args, timeout):
        var01 = fname
        var02 = f"{args}"
        var03 = timeout
        self.args('', var01, var02, var03,task_name=True)


if __name__ =="__main__":
    from Qrepeater.utils.log_color import ColorLog
    logger = ColorLog('test','green')
    
    tracer = Msg(logger, 'async')
    tracer.info.exception('dd',(2,3),3)
