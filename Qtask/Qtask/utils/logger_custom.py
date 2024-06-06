# -------------------------------- ver 240510 -------------------------------- #
# -------------------------------- ver 240511 -------------------------------- #
# def ith(prefix:str)
# -------------------------------- ver 240606 -------------------------------- #
# def clsname
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
    def __init__(self, 
                 logger:logging.Logger,
                 clsname:str,
                 context:Literal['sync', 'thread', 'async'] = 'sync'):

        self.logger = logger
        self.clsinst = f"{clsname:<7} - {self.logger.name:<7} | "

        if context == 'sync':
            self.method = _Sync()
        elif context =='thread':
            self.method = _Thread()
        elif context == 'async':
            self.method = _Async()

    def msg(self, status, *args, frame:int|str|None=1, task=False, offset:float|None=None):
        """>>> #{func.status:<20} {arg:12}"""
        # -------------------------------------------------------------------- #
        #                                header                                #
        # -------------------------------------------------------------------- #
        
        str_frame = self._get_frame(frame=frame)
        str_status = status
        HEADER = self.clsinst + self._get_header(status=str_status,frame=str_frame)

        # -------------------------------------------------------------------- #
        #                                 body                                 #
        # -------------------------------------------------------------------- #
        str_args = ', '.join([f"{arg:<12}" for arg in args]) 
        BODY = f" | {str_args:<40}" 

        # -------------------------------------------------------------------- #
        #                                footter                               #
        # -------------------------------------------------------------------- #
        str_task = f" | {asyncio.current_task().get_name():<10}" if task else ""
        str_offset = self._get_offset(offset) if offset is not None else ""
        FOOTTER = f"{str_offset}{str_task}"
        # ------------------------------- final ------------------------------ #
        LOG_MSG = f"{HEADER}{BODY}{FOOTTER}"
        self._log_chained(LOG_MSG) 

    def div(self, task=False, offset:float|None=None):
        BODY = f"{'='*81}"
        str_task = f" | {asyncio.current_task().get_name():<10}" if task else ""
        str_offset = self._get_offset(offset) if offset is not None else ""
        FOOTTER = f"{str_offset}{str_task}"
        DIV_MSG = f"{BODY}{FOOTTER}"
        self._log_chained(DIV_MSG) 

    def arg(self, text, width:Literal[1,2,3],align:Literal['left','right']='Left', fill="="):
        if width ==1:
            w=12
        elif width ==2:
            w=26
        else:
            w=40
        if align in ['left','l']:
            t = f"{text:<{w}}"
        elif align in ['right','r']:
            t = f"{text:>{w}}"

        return t.replace(" ", fill)

    def ith(self, prefix:str=None):
        if prefix is None:
            prefix = self.logger.name

        tasks = [t.get_name() for t in asyncio.all_tasks() if t.get_name().startswith(prefix)]
        # print(tasks)
        if tasks :
            used = [int(t.get_name().split('-')[-1]) for t in asyncio.all_tasks() if t.get_name().startswith(prefix)]
            newi = next((x for x in range(max(used) + 10) if x not in used),0)
        else:
            newi = 0
        return f"{prefix}-{newi}"

    def _get_frame(self, frame):
        if frame is None:
            rslt = ""
        elif isinstance(frame , str):
            rslt = frame
        elif isinstance(frame, int):
            n_back = frame + 1
            cframe = inspect.currentframe()
            for _ in range(n_back):
                cframe = cframe.f_back
            rslt = cframe.f_code.co_name
        return rslt
    
    def _get_header(self, status, frame):
        nspace = 18 - (len(frame) +len(status))
        return f"{frame}{'.' * nspace}{status}"
    
    def _get_offset(self, offset:float):
        server_now = datetime.now() + timedelta(seconds=offset)
        server = f" | {server_now.strftime('%H:%M:%S')},{server_now.strftime('%f')[:3]}({offset:+.4f})"
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
    logger = logging.getLogger('mylog')
    logger.setLevel(logging.DEBUG) 
    handler = logging.StreamHandler() 
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-7s | %(message)-40s | [%(threadName)s]')
    formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)-40s | [%(threadName)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    print('# ------------------------------- functions ------------------------------- #')
    customlog = CustomLog(logger, 'Myclass')
    customlog.msg('args','val1') 
    customlog2 = CustomLog(logger, 'Myclas')
    customlog2.msg('args','val1','val2') 
    customlog2.msg('args','val1','val2','val3') 
    customlog2.msg('text','looooooooooooooooooooooooooooooooong')

    print('# --------------------------------- chain -------------------------------- #')
    customlog.msg('args','val1','val2','val3')
    customlog.info.msg('args','val1','val2','val3')
    customlog.warning.msg('args','val1','val2','val3')

    print('# --------------------------------- frame -------------------------------- #')
    def func_inner(frame):
        customlog.info.msg('args','val1','val2','val3',frame=frame)
        customlog.info.msg('test','val1','val2','val3',frame='dddd')

    def func_outter(frame):
        func_inner(frame)

    func_outter(frame=1)
    func_outter(frame=2)
    func_inner(frame=None)



    print('# -------------------------------- offset -------------------------------- #')
    customlog.info.msg('offset', 'task',offset=0.02)
    
    print('# ---------------------------------- task -------------------------------- #')
    async def main():
        customlog.info.msg('async', 'task',task=True)
        customlog.info.msg('async', 'task',task=True, offset=0.1)
    asyncio.run(main())

    print('# ---------------------------------- div --------------------------------- #')
    customlog.info.div()
    customlog.info.div(offset=0.1)

    print('# ---------------------------------- arg --------------------------------- #')

    customlog.info.msg('test', "hi", customlog.arg("left",1,'left',"-"))
    customlog.info.msg('test', "hi", customlog.arg("left",2,'left',"-"))
    customlog.info.msg('test', "hi", customlog.arg("left",2,'r',"-"))