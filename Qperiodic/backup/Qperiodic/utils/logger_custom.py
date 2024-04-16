import threading
import contextvars
import inspect
from typing import Literal
import logging
import asyncio
# ---------------------------------------------------------------------------- #
#                                   customlog                                  #
# ---------------------------------------------------------------------------- #
class CustomLog:
    """>>> #
    customlog.msg(status, *args, task_name=True, n_back=1)
    """
    def __init__(self, logger:logging.Logger,
                 context:Literal['sync', 'thread', 'async'] = 'sync'):
        self.logger = logger
        if context == 'sync':
            self.method = _Sync()
        elif context =='thread':
            self.method = _Thread()
        elif context == 'async':
            self.method = _Async()
            
    def msg(self, status, *args, task=False, back:int=1):
        """>>> #{func.status:<20} {arg:12}"""
        frame = self._get_frame(n_back=back+1) if back is not None else ""
        header = self._get_header(status=status,frame=frame)
        text = ', '.join([f"{arg:<12}" for arg in args]) 
        body = " | "f"{text:<40}" +" |"
        if task: body = body+f" {asyncio.current_task().get_name():<10}"
        self._log_chained(header + body) 

    def _get_frame(self, n_back=1):
        frame = inspect.currentframe()
        for _ in range(n_back):
            frame = frame.f_back
        return frame.f_code.co_name
    
    def _get_header(self, status, frame):
        nspace = 18 - (len(frame) +len(status))
        return f"{frame}{'.' * nspace}{status}"
    
    def _log_chained(self, msg):
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
    import asyncio
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG) 
    handler = logging.StreamHandler() 
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)7s @ %(name)7s . %(message)s [%(threadName)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print('# ------------------------------- functions ------------------------------- #')
    customlog = CustomLog(logger, 'sync')
    customlog.msg('args','val1') 
    customlog.msg('args','val1','val2') 
    customlog.msg('args','val1','val2','val3') 
    customlog.msg('text','looooooooooooooooooooooooooooooooong')

    print('# --------------------------------- chain -------------------------------- #')
    customlog.msg('args','val1','val2','val3')
    customlog.info.msg('args','val1','val2','val3')
    customlog.warning.msg('args','val1','val2','val3')

    print('# ---------------------------------- back -------------------------------- #')
    def func_inner(back):
        customlog.info.msg('args','val1','val2','val3',back=back)

    def func_outter(back):
        func_inner(back)

    func_outter(back=1)
    func_outter(back=2)
    
    print('# ---------------------------------- task -------------------------------- #')
    async def main():
        customlog.info.msg('async', 'task',task=True)

    asyncio.run(main())


