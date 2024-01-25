import threading
import contextvars
import inspect
from typing import Literal
import logging

class CustomLog:
    def __init__(self, logger:logging.Logger,
                 context:Literal['sync', 'thread', 'async'] = 'sync'):
        self.logger = logger
        if context == 'sync':
            self.method = _Sync()
        elif context =='thread':
            self.method = _Thread()
        elif context == 'async':
            self.method = _Async()

    def stream(self, status, *args):
        """>>> #{func.status:<20} {arg:12}"""
        # frame = f'{inspect.stack()[2].function}.{status}'
        frame = f'{inspect.currentframe().f_back.f_code.co_name}.{status}'
        header = f'{frame:<20} ::: '
        body = ', '.join([f"{arg:<12}" for arg in args]) +" :::"
        self.msg(header + body) 

    def msg(self, msg):
        if self.logger is not None:
            self.log(msg=msg)

    def log(self, msg):
        self.logger.log(level=self.method.level, msg=msg)

    @property
    def debug(self):
        self.method.level = logging.DEBUG
        return self

    @property
    def info(self):
        self.method.level = logging.INFO
        return self
    
    @property
    def warning(self):
        self.method.level = logging.WARNING
        return self

    @property
    def error(self):
        self.method.level = logging.ERROR
        return self

class _Sync:

    def __init__(self):
        self._level = logging.DEBUG
    @property
    def level(self):
        return self._level
    
    @level.setter
    def level(self, value):
        self._level = value

class _Thread:

    def __init__(self):
        self._level = threading.local()
    @property
    def level(self):
        return self._level.value
    
    @level.setter
    def level(self, value):
        self._level.value = value
    
class _Async:
    def __init__(self):
        self._level = contextvars.ContextVar('level')
    @property
    def level(self):
        return self._level.get()
    
    @level.setter
    def level(self, value):
        self._level.set(value)

if __name__ == "__main__":
    print('# --------------------------------- green -------------------------------- #')
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG) 
    handler = logging.StreamHandler() 
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)7s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    chain = CustomLog(logger, 'sync')
    chain.msg('default debug')
    chain.info.msg('info')
    chain.debug.msg('debug')
    chain.warning.msg('warning')
    chain.error.msg('error')

    def test():
        chain.stream('status','(1234567890)','(1234567890)','(1234567890)')
    test()

    print('# ------------------------------- customlog ------------------------------ #')

    class Msg(CustomLog):

        def msg_module01(self):
            self.stream('mod01', 'init', 'test_custom')

        def msg_module02(self):
            self.stream('mod02', 'start', 'test_custom')
    
    mylogger = Msg(logger, 'sync')
    mylogger.info.msg_module01()
    mylogger.debug.msg_module02()