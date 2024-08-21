# -------------------------------- ver 240811 -------------------------------- #
# msg_fname_task
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

def _trunc_char(main:str, nchar:int, subfix:str="*"):
    if len(main) > nchar:
        rslt = main[:(nchar-len(subfix))] + str(subfix)
    else:
        rslt = main
    return rslt

def msg_header(main:str, sub:str, nchar=23, sep='.'):
    n_over = max(len(main) + len(sub) + 2 - nchar ,0)
    n_over_main = int(n_over * len(main)/nchar)
    n_over_sub = n_over - n_over_main

    main_cut = _trunc_char(main,len(main)-n_over_main)
    sub_cut = _trunc_char(sub,len(sub)-n_over_sub)

    mid = sep * (nchar - len(main_cut) - len(sub_cut)-2)
    rslt = f"{main_cut}{mid}[{sub_cut}]"
    return rslt

def msg_fname(fname:int|str=2, nchar=23, sep='.'):
    if isinstance(fname, int):
        cframe = inspect.currentframe()
        for _ in range(fname):
            cframe = cframe.f_back
        func_name = cframe.f_code.co_name
    else:
        func_name = fname

    rslt = _trunc_char(func_name,nchar-2,subfix='*')+"()"
    rslt = f"{rslt:{sep}<{nchar}}"
    return rslt

def msg_fname_task(fname:int|str=2, nchar=23, sep='.'):
    # ------------------------------- task name ------------------------------ #
    try:
        task_name = asyncio.current_task().get_name()+'.'
    except Exception as e:
        task_name = '(main).'
    # ------------------------------- func name ------------------------------ #
    if isinstance(fname, int):
        cframe = inspect.currentframe()
        for _ in range(fname):
            cframe = cframe.f_back
        func_name = cframe.f_code.co_name
    else:
        func_name = fname
    
    # -------------------------------- gen msg ------------------------------- #
    main = task_name
    sub = func_name
    n_over = max(len(main) + len(sub) + 2 - nchar ,0)
    # n_over_main = int(n_over * len(main)/nchar)
    n_over_main = 0
    n_over_sub = n_over - n_over_main

    main_cut = _trunc_char(main,len(main)-n_over_main)
    sub_cut = _trunc_char(sub,len(sub)-n_over_sub)

    mid = sep * (nchar - len(main_cut) - len(sub_cut)-2)
    rslt = f"{main_cut}{mid}{sub_cut}()"

    rslt = f"{rslt:{sep}<{nchar}}"
    return rslt


def msg_footter(offset:float):
    server_now = datetime.now() + timedelta(seconds=offset)
    server = f"{server_now.strftime('%H:%M:%S')},{server_now.strftime('%f')[:3]}({offset:+.3f})"
    return server

def msg_debugvar(debug_var, nchar=15, sep='-'):
    debug_var = _trunc_char(f" {debug_var}",nchar,subfix='*')
    rslt = f"{debug_var:{sep}>{nchar-1}}"
    return rslt

def msg_body(*args, widths:tuple=None,aligns:tuple=None,paddings:tuple=None, nchar=23):
    # -------------------------------- widths -------------------------------- #
    if widths is None:
        if len(args) == 1:
            widths = (3,)
        elif len(args) == 2:
            widths = (1,2)
        else:
            widths = len(args)*[1]
    elif isinstance(widths,int):
        widths=(widths,)
    # -------------------------------- aligns -------------------------------- #
    if aligns is None:
        aligns = len(args)*["<"]
    elif aligns in ["^",">","<"]:
        aligns = len(args)*[aligns]
    # -------------------------------- padding ------------------------------- #
    if paddings is None:
        paddings = len(args)*[" "]
    elif isinstance(paddings, str):
        paddings = len(args)*[str(paddings)]

    # -------------------------------- result -------------------------------- #
    result=[]
    for arg,width,align,pad in zip(args,widths,aligns,paddings):
        if isinstance(arg, tuple):
            result.append(arg_sep(arg[0],arg[1],nchar))
        else:
            arg = str(arg)
            wid = width*nchar+(width-1)*2
            txt = arg[:(wid-1)]+"*" if len(arg)>wid else arg
            alg = f"{pad}{align}{wid}"
            # print(alg)
            result.append(f"{txt:{alg}}")
    return ', '.join(result) 

def arg_sep(arg1:str, arg2:str, nchar=23, sep=' '):
    n_over = max(len(arg1) + len(arg2) - nchar ,0)
    n_over_main = int(n_over * len(arg1)/nchar)
    n_over_sub = n_over - n_over_main

    arg1_cut = _trunc_char(arg1,len(arg1)-n_over_main)
    arg2_cut = _trunc_char(arg2,len(arg2)-n_over_sub)

    mid = sep * (nchar - len(arg1_cut) - len(arg2_cut))
    rslt = f"{arg1_cut}{mid}{arg2_cut}"
    return rslt

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
