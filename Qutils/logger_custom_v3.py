# -------------------------------- ver 240510 -------------------------------- #
# -------------------------------- ver 240511 -------------------------------- #
# def ith(prefix:str)
# -------------------------------- ver 240606 -------------------------------- #
# def clsname
# -------------------------------- ver 240617 -------------------------------- #
# v3
# -------------------------------- ver 240624 -------------------------------- #
# size 15 and cls
# -------------------------------- ver 240629 -------------------------------- #
# arg = str(arg)
# -------------------------------- ver 240702 -------------------------------- #
# getlogger
# ---------------------------------------------------------------------------- #
from datetime import datetime, timedelta
import os
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
                 context:Literal['thread', 'async','module'] = 'module'):

        self.logger = logger 

        self.CLASS = self._get_CLASS(cla=clsname, log=self.logger.name)
        self.mode = context

        if context == 'module':
            self.method = _Module()
        elif context =='thread':
            self.method = _Thread()
        elif context == 'async':
            self.method = _Async()
            
    # ------------------------------------------------------------------------ #
    #                                  public                                  #
    # ------------------------------------------------------------------------ #
    def msg(self, *args, widths:tuple=None,aligns:tuple=None,paddings:tuple=None,
            frame:int|str|None=1, mode:Literal['thread','async','module']=None, 
            offset:float|None=None,module:int=2):
        """>>> # 
        align : Literal["^","<",">"]
        padding : default (" ") 
        frame : int (1) n_back
        module : mode ('module') n_back"""
        # 2024-06-17 07:53:02,515 | INFO    | Mycladdd....(mylodg) | dddd..........test | val1        , val2        , val3         | [MainThread]
        # 40 | 7 | 20 | 20 |
        CLASS = self.CLASS
        HEADER = self._get_HEADER(mode,frame,module)
        BODY = self._get_BODY(*args, widths=widths,aligns=aligns,paddings=paddings)
        FOOTTER = self._get_FOOTTER(offset)
        LOG_MSG = f"{CLASS}{HEADER}{BODY}{FOOTTER}"
        self._log_chained(LOG_MSG) 

    def ini(self, name):
        self.info.msg(name, widths=(3,),aligns=(">"),paddings=('-'))

    def div(self, offset:float|None=None):
        BODY = f"{'='*95}"
        FOOTTER = self._get_FOOTTER(offset)
        DIV_MSG = f"{BODY}{FOOTTER}"
        self._log_chained(DIV_MSG) 

    def max(self, text, offset:float|None=None):
        BODY = f"{str(text):<95}"
        FOOTTER = self._get_FOOTTER(offset)
        DIV_MSG = f"{BODY}{FOOTTER}"
        self._log_chained(DIV_MSG) 

    def cls(self, text, offset:float|None=None):
        CLASS = self.CLASS
        BODY = f"{str(text):<72}"
        FOOTTER = self._get_FOOTTER(offset)
        DIV_MSG = f"{CLASS}{BODY}{FOOTTER}"
        self._log_chained(DIV_MSG) 

    # ------------------------------------------------------------------------ #
    #                                   main                                   #
    # ------------------------------------------------------------------------ #
    def _get_CLASS(self, cla, log):
        return self._get_lr(20,'.',cla,f"({log})") + " | "
    
    def _get_HEADER(self, mode:Literal['thread','async','module'], frame:int|str|None=1, module:int=2):
        mode = self.mode if mode is None else mode
        left = self._get_mode(mode, module=module)
        righ = self._get_call(frame)
        return self._get_lr(20,'.',left,righ) + " | "

    def _get_FOOTTER(self, offset:float=None):
        if offset is None :
            str_offset =  ""
        else:
            str_offset = self._get_offset(offset=offset)

        footter = str_offset

        return " | "+ str_offset if footter != "" else ""
    
    def _get_BODY(self, *args, widths:tuple=None,aligns:tuple=None,paddings:tuple=None):
        """>>> align : Literal["^","<",">"]
        padding : default (" ")"""

        str_args = self._get_args(*args, widths=widths,aligns=aligns,paddings=paddings)

        return str_args
    # ------------------------------------------------------------------------ #
    #                                    sub                                   #
    # ------------------------------------------------------------------------ #

    def _get_args(self, *args, widths:tuple=None,aligns:tuple=None,paddings:tuple=None):
        result=[]
        # widths = len(args)*[1] if widths is None else widths

        if widths is None:
            if len(args) == 1:
                widths = (3,)
            elif len(args) == 2:
                widths = (1,2)
            else:
                widths = len(args)*[1]
        elif isinstance(widths,int):
            widths = len(args)*[widths]

        if aligns is None:
            aligns = len(args)*["<"]
        elif aligns in ["^",">","<"]:
            aligns = len(args)*[aligns]

        if paddings is None:
            paddings = len(args)*[" "]
        elif len(str(paddings))==1:
            paddings = len(args)*[str(paddings)]

        for arg,width,align,pad in zip(args,widths,aligns,paddings):
            arg = str(arg)
            wid = width*15+(width-1)*2
            txt = arg[:(wid-1)]+"*" if len(arg)>wid else arg
            alg = f"{pad}{align}{wid}"
            # print(alg)
            result.append(f"{txt:{alg}}")
        return ', '.join(result) 
    
    def _get_lr(self, total,sep,left,right):
        left_cut = left if len(left)<=10 else left[:9]+"*"
        right_cut = right if len(right)<=10 else right[:9]+"*"
        mid = sep * (total - len(left_cut) - len(right_cut))
        return f"{left_cut}{mid}{right_cut}"

    def _get_offset(self, offset:float):
        server_now = datetime.now() + timedelta(seconds=offset)
        server = f"{server_now.strftime('%H:%M:%S')},{server_now.strftime('%f')[:3]}({offset:+.3f})"
        return server

    def _get_call(self, frame):
        if frame is None:
            rslt = ""
        elif isinstance(frame , str):
                rslt = frame
        elif isinstance(frame, int):
            n_back = frame + 2
            cframe = inspect.currentframe()
            for _ in range(n_back):
                cframe = cframe.f_back
            rslt = cframe.f_code.co_name
        return rslt        

    def _get_mode(self, mode:Literal['thread','async','module'], module:int=2):
        try:
            if mode == 'thread':
                rslt = threading.current_thread().name
            elif  mode == 'async':
                rslt = asyncio.current_task().get_name()
            elif mode =='module':
                n_back = module + 2
                cframe = inspect.currentframe()
                for _ in range(n_back):
                    cframe = cframe.f_back
                rslt = inspect.getmodule(cframe).__name__.split(".")[-1]
        except Exception as e:
            n_back = module + 2
            cframe = inspect.currentframe()
            for _ in range(n_back):
                cframe = cframe.f_back
            rslt = inspect.getmodule(cframe).__name__.split(".")[-1]
            # caller_frame = inspect.stack()[3]
            # caller_module = inspect.getmodule(caller_frame[0])
            # rslt = os.path.basename(caller_module.__file__).split(".")[0]
        return rslt



    # --------------------------------- stub --------------------------------- #
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

    
    def _log_chained(self, msg):
        if self.logger is not None:
            self.logger.log(level=self.method.level, msg=msg)

    @staticmethod
    def getlogger(name:str):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG) 
        handler = logging.StreamHandler() 
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)-40s |')
        handler.setFormatter(formatter)
        if logger.hasHandlers(): logger.handlers.clear()
        logger.addHandler(handler)
        return logger


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
class _Module:
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
# import asyncio
# logger = logging.getLogger('mylodg')
# logger.setLevel(logging.DEBUG) 
# handler = logging.StreamHandler() 
# handler.setLevel(logging.DEBUG)
# # formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-7s | %(message)-40s | [%(threadName)s]')
# formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)-40s |')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# customlog = CustomLog(logger, 'CLASS')
# def myfun():
#     customlog.info.m('a','b','c')
# myfun()
# | CLASS.......(mylodg) | __main__.......myfun | a                                        |
# | a                                        |
# | CLASS.......(mylodg) | __main__.......myfun | a                                           | 10:58:04,868(+0.100) |
# | a                                           |
if __name__ == "__main__":
    import asyncio
    logger = logging.getLogger('mylodg')
    logger.setLevel(logging.DEBUG) 
    handler = logging.StreamHandler() 
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)-7s | %(message)-40s | [%(threadName)s]')
    formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(message)-40s |')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    customlog = CustomLog(logger, 'CLASS')
    def myfun():
        customlog.info.msg('a','b','c',offset=0.1)
        customlog.info.msg('a',offset=0.1)
        customlog.info.msg('a','b',offset=0.1)
        customlog.info.msg('a','b','c',offset=0.1)
        customlog.info.msg('a','b',widths=(2,1),offset=0.1)
        customlog.info.msg('a',widths=(3,),offset=0.1)
        customlog.debug.msg('a',widths=(3,),offset=0.1)
        customlog.debug.msg('a',widths=(3,))
        customlog.debug.div(offset=0.1)
        customlog.debug.max('a'*20)
        customlog.debug.cls('cls'*20)
        customlog.info.msg('a','b','c',aligns='>',paddings="-",offset=0.1)
        customlog.info.msg('addddddddddddddd','b',widths=(1,2),aligns=("<",">"),paddings=(" ","-"),offset=0.1)

    myfun()

    print(len("2024-06-17 11:00:30,723 | ERROR   | CLASS.......(mylodg) | __main__.......myfun | a                                           | 11:00:30,823(+0.100) |"))
    print(len("2024-06-17 11:00:30,723 | ERROR   | CLASS.......(mylodg) | __main__.......myfun | a                                           |"))

    # print('# ------------------------------- functions ------------------------------- #')
    # customlog = CustomLog(logger, 'Mycladdd')
    # customlog.msg('args','val1') 
    # customlog2 = CustomLog(logger, 'Myclas')
    # customlog2.msg('args','val1','val2') 
    # customlog2.msg('args','val1','val2','val3') 
    # customlog2.msg('text','looooooooooooooooooooooooooooooooong')

    # print('# --------------------------------- chain -------------------------------- #')
    # customlog.msg('args','val1','val2','val3')
    # customlog.info.msg('args','val1','val2','val3')
    # customlog.warning.msg('args','val1','val2','val3')

    # print('# --------------------------------- frame -------------------------------- #')
    # def func_inner(frame):
    #     customlog.info.msg('args','val1','val2','val3',frame=frame)
    #     customlog.info.msg('test','val1','val2','val3',frame='dddd')

    # def func_outter(frame):
    #     func_inner(frame)

    # func_outter(frame=1)
    # func_outter(frame=2)
    # func_inner(frame=None)



    # print('# -------------------------------- offset -------------------------------- #')
    # customlog.info.msg('offset', 'task',offset=0.02)
    
    # print('# ---------------------------------- task -------------------------------- #')
    # async def main():
    #     customlog.info.msg('async', 'task',task=True)
    #     customlog.info.msg('async', 'task',task=True, offset=0.1)
    # asyncio.run(main())

    # print('# ---------------------------------- div --------------------------------- #')
    # customlog.info.div()
    # customlog.info.div(offset=0.1)

    # print('# ---------------------------------- arg --------------------------------- #')

    # customlog.info.msg('test', "hi", customlog.arg("left",1,'left',"-"))
    # customlog.info.msg('test', "hi", customlog.arg("left",2,'left',"-"))
    # customlog.info.msg('test', "hi", customlog.arg("left",2,'r',"-"))

    # print('# --------------------------------- full --------------------------------- #')
    # customlog.info.full("ddddddddddddddddddddddddddddddddddddddddddddddd")