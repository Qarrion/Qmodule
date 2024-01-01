from logging import Logger
from typing import Literal
from Qlogger import Logger, CustomLog
import inspect

class Msg(CustomLog):
    def __init__(self, logger: Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def stream(self, status, *args):
        # frame = f'{inspect.stack()[2].function}.{status}'
        frame = f'{inspect.currentframe().f_back.f_code.co_name}.{status}'
        header = f'/{frame:<20} ::: '
        body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
        self.msg(header + body)


if __name__ == "__main__":

    logger = Logger('logger1','blue','default.ini',debug=False)

    logger.debug('hi')

    msg = Msg(logger)
    class clss:
        def myfunc(self):
            msg.info.stream('status')
    clss().myfunc()
    # myfunc()