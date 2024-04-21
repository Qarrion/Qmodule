from datetime import datetime, timedelta
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

    def msg(self, status, *args, task=False, frame:int|None=1, offset:float|None=None):
        """>>> #{func.status:<20} {arg:12}"""
        # -------------------------------------------------------------------- #
        #                                header                                #
        # -------------------------------------------------------------------- #
        str_frame = self._get_frame(n_back=frame+1) if frame is not None else ""
        str_status = status

        HEADER = self._get_header(status=str_status,frame=str_frame)
        # -------------------------------------------------------------------- #
        #                                 body                                 #
        # -------------------------------------------------------------------- #
        str_args = ', '.join([f"{arg:<12}" for arg in args]) 
        
        BODY = f" | {str_args:<40} |" 
        
        # -------------------------------------------------------------------- #
        #                                footter                               #
        # -------------------------------------------------------------------- #
        str_task = f" {asyncio.current_task().get_name():<10}" if task else ""
        str_offset = self._get_offset(offset) if offset is not None else ""

        FOOTTER = f"{str_task}{str_offset}"
        # if offset is not None : 
            
        LOG_MSG = f"{HEADER}{BODY}{FOOTTER}"
        self._log_chained(LOG_MSG) 

    # def msg_offset(self, status, *args, task=False, back:int=1):
    #     """>>> #{func.status:<20} {arg:12}"""
    #     frame = self._get_frame(n_back=back+1) if back is not None else ""
    #     header = self._get_header(status=status,frame=frame)
    #     text = ', '.join([f"{arg:<12}" for arg in args]) 

    #     offset = self.core.offset
    #     server_now = datetime.now() + timedelta(seconds=offset)
    #     server = f"{server_now.strftime('%Y-%m-%d %H:%M:%S')},{server_now.strftime('%f')[:3]}({offset:+.4f})"
    #     body = f" | {text:<40} | {server}" 
    #     if task: body = body+f" {asyncio.current_task().get_name():<10}"
        
    #     self._log_chained(header + body) 

    def _get_frame(self, n_back=1):
        frame = inspect.currentframe()
        for _ in range(n_back):
            frame = frame.f_back
        return frame.f_code.co_name
    
    def _get_header(self, status, frame):
        nspace = 18 - (len(frame) +len(status))
        return f"{frame}{'.' * nspace}{status}"
    
    def _get_offset(self, offset:float):
        server_now = datetime.now() + timedelta(seconds=offset)
        server = f" {server_now.strftime('%Y-%m-%d %H:%M:%S')},{server_now.strftime('%f')[:3]}({offset:+.4f})"
        return server
    
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

    print('# --------------------------------- frame -------------------------------- #')
    def func_inner(frame):
        customlog.info.msg('args','val1','val2','val3',frame=frame)

    def func_outter(frame):
        func_inner(frame)

    func_outter(frame=1)
    func_outter(frame=2)
    func_inner(frame=None)
    
    print('# ---------------------------------- task -------------------------------- #')
    async def main():
        customlog.info.msg('async', 'task',task=True)
    asyncio.run(main())

    print('# -------------------------------- offset -------------------------------- #')
    customlog.info.msg('offset', 'task',offset=0.02)



