import threading
import contextvars
import inspect
from typing import Literal
import logging

# ---------------------------------------------------------------------------- #
#                                   customlog                                  #
# ---------------------------------------------------------------------------- #
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
            
    def get_frame(self, n_back=1):
        frame = inspect.currentframe()
        for _ in range(n_back):
            frame = frame.f_back
        return frame.f_code.co_name
    
    def get_header(self,status, frame):
        header = f'{frame} / {status}'
        return  f'{header:<20}'
    
    def args(self, status, *args, n_back=1):
        """>>> #{func.status:<20} {arg:12}"""
        frame = self.get_frame(n_back=n_back+1)
        header = self.get_header(status=status,frame=frame)
        text = ', '.join([f"{arg:<12}" for arg in args]) 
        body = "::: "f"{text:<40}" +" :::"
        self.log(header + body) 

    def text(self, status, text, n_back=1):
        """>>> #{func.status:<20} {text:40}"""
        frame = self.get_frame(n_back=n_back+1)
        header = self.get_header(status=status,frame=frame)
        body = "::: "f"{text:<40}" +" :::"
        self.log(header + body) 

    def log(self, msg):
        if self.logger is not None:
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

# ---------------------------------------------------------------------------- #
#                                     local                                    #
# ---------------------------------------------------------------------------- #
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

# ---------------------------------------------------------------------------- #
#                                     main                                     #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":

    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG) 
    handler = logging.StreamHandler() 
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)7s @ %(name)7s . %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print('# --------------------------------- chain -------------------------------- #')
    clogger = CustomLog(logger, 'sync')
    clogger.args('args','val1','val2','val3')
    clogger.info.args('args','val1','val2','val3')
    clogger.warning.args('args','val1','val2','val3')

    print('# ------------------------------- function ------------------------------- #')
    clogger.args('args','val1','val2','val3')
    clogger.args('args','val1','val2')
    clogger.text('text','text'*5)

    print('# --------------------------------- nback -------------------------------- #')
    class Myclass:
        def myfunc1(self):
            clogger.info.args('args','val1','val2','val3',n_back=1)
        
        def myfunc2(self):
            clogger.debug.args('args','val1','val2','val3',n_back=2)

    myclass = Myclass()
    myclass.myfunc1()
    myclass.myfunc2()


    print('# ------------------------------ superclass ------------------------------ #')
    class Msg(CustomLog):
        def msg_module01(self, status, *args, n_back=1):
            self.args(status, *args, n_back=n_back)

    class Myclass2:
        def __init__(self, logger):
            self.msg = Msg(logger)

        def myfunc1(self):
            self.msg.msg_module01('args','val1','val2','val3', n_back=1)
        
        def myfunc2(self):
            self.msg.msg_module01('args','val1','val2','val3', n_back=2)

    myclass2 = Myclass2(logger)
    myclass2.myfunc1()
    myclass2.myfunc2()
    