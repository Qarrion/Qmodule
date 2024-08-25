import asyncio
from typing import Literal
from Qlogger.config import Config
from Qlogger.utils.custom_print import cmap
from Qlogger import function
import logging

hint = Literal['level','head','red','green','yellow','blue','reset']

level = {
    'WARNING':  cmap['yellow'],
    'INFO':     cmap['green'],
    'DEBUG':    cmap['blue'],
    'CRITICAL': cmap['red'],
    'ERROR':    cmap['red'],
    'RESET':    cmap['reset'],
}

class _Logger(logging.Logger):
    def __init__(self, name:str, color:hint='reset', inifile='log.ini',msg=False):
        super().__init__(name, level=logging.NOTSET)
        config = Config(filename=inifile,msg=msg)

        log_lev = config.get(section=name, option='level')
        log_fmt = config.get(section=name, option='fmt', raw=True)
        log_ymd = config.get(section=name, option='datefmt', raw=True, fallback=None)

        # ----------------------------- formatter ---------------------------- #
        if color == 'level':
            formatter = LevelFormatter(fmt=log_fmt, datefmt=log_ymd)
        elif color == 'head':
            formatter = HeadFormatter(fmt=log_fmt, datefmt=log_ymd)
        else:
            # if color is None : color = 'reset'
            log_fmt_col = f"{cmap[color]}{log_fmt}{cmap['reset']}"
            formatter = logging.Formatter(fmt=log_fmt_col, datefmt=log_ymd)
    
        # -------------------------- stream_handler -------------------------- #
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_lev)

        if self.hasHandlers(): self.handlers.clear()        
        self.addHandler(stream_handler)  

    def _dev_stream_handler_level(self, log_lev:Literal['DEBUG','INFO','WARNING','ERROR']):
        """change stream_handler log level"""
        for handler in self.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(log_lev)

class LevelFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        original_formatted_log = super().format(record)

        level_color = level.get(record.levelname, cmap['reset'])
        colored_log = f"{level_color}{original_formatted_log}{cmap['reset']}"
        return colored_log
    
class HeadFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        original_formatted_log = super().format(record)

        level_color = level.get(record.levelname, cmap['reset'])
        levelname_with_color = f"{level_color}{record.levelname}{cmap['reset']}"

        colored_log = original_formatted_log.replace(record.levelname, levelname_with_color)
        return colored_log

# ---------------------------------------------------------------------------- #
#                                 CustomLogger                                 #
# ---------------------------------------------------------------------------- #
class Logger(_Logger):

    def __init__(self, logname:str, clsname:str='Logger', color:hint='head', context:Literal['sync','async','thread']='sync', 
                 inifile='log.ini',msg=False):
        super().__init__(logname, color, inifile, msg)
        self._logname = logname
        self._clsname = clsname
        self._context = context

        if context == 'sync':
            self._method = function._Sync()
        elif context =='thread':
            self._method = function._Thread()
        elif context == 'async':
            self._method = function._Async()

    def set_clsname(self, clsname:str):
        self._clsname = clsname

    def set_sublogger(self, sublogger:_Logger):
        sublogger._clsname = self._clsname
        sublogger._logname = f"{self._logname}.{sublogger._logname}"
        sublogger._context = self._context

    def msg(self, *args, widths:tuple=None, aligns:tuple=None, paddings:tuple=None, nchar=23,
            fname:int|str=2, offset:float=None, mode:int=0, debug_var=None):
        """ + aligns : ^,<,>
        + mode : 0(header,fname,body),
        + mode : 1(fname,body),
        + mode : 2(func,body)
        + mode : 3(body)
        """
        HEADER = function.msg_header(main = self._clsname, sub=self._logname,nchar=23, sep='.')
        if self._context == 'sync':
            FNAME = function.msg_fname(fname=fname,nchar=23,sep='.')
        elif self._context == 'async':
            FNAME = function.msg_fname_task(fname=fname,nchar=23,sep='.')

        BODY = function.msg_body(*args,widths=widths,aligns=aligns,paddings=paddings,nchar=nchar)

        if mode == 0:
            LOG_MSG = f"{HEADER} | {FNAME} | {BODY}"
        elif mode==1:
            LOG_MSG = f"{FNAME} | {BODY}"
        elif mode==2:
            LOG_MSG = f"{HEADER} | {BODY}"
        elif mode==3:
            LOG_MSG = f"{BODY}"

        if debug_var is not None:
            FOOTTER =  function.msg_debugvar(debug_var=debug_var)
            LOG_MSG= f"{LOG_MSG} | {FOOTTER}"

        if offset is not None:
            FOOTTER =  function.msg_footter(offset=offset)
            LOG_MSG= f"{LOG_MSG} | {FOOTTER}"

        self.log(level=self._method.level, msg=LOG_MSG)

    def div(self, sep="=", nchar=23, args:int=3, offset:float=None):
        LOG_MSG = f"{sep*nchar}==={sep*nchar} | {sep*(nchar*args+(args-1)*2)}"

        if offset is not None:
            FOOTTER =  function.msg_footter(offset=offset)
            LOG_MSG= f"{LOG_MSG} | {FOOTTER}"
        self.log(level=self._method.level, msg=LOG_MSG)
        
    @property
    def debug(self):
        self._method.level = logging.DEBUG
        return self

    @property
    def info(self):
        self._method.level = logging.INFO
        return self
    
    @property
    def warning(self):
        self._method.level = logging.WARNING
        return self

    @property
    def error(self):
        self._method.level = logging.ERROR
        return self
    

if __name__ == "__main__":

    # ------------------------------ base logger ----------------------------- #
    logger = _Logger('test', 'head', 'log.ini', msg=True)
    logger.debug('debug')
    logger.info('info')
    logger.warning('warn')
    logger.error('error')

    # ----------------------------- custom logger ---------------------------- #

    logger = Logger('test','head',context='async')
    logger.set_clsname('child')

    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bbbbbbbbbbbbbbbbbbbbbbbbbb',)
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',paddings='-')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='^')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='<')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns='>')
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bb','cc',aligns=['^','<','>'])
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa','bbbbbbbbbbbbbbbbbbbbbbbbbb',widths=(2,1))
    # logger.info.msg('aaaaaaaaaaaaaaaaaaaaaaaaa')
    # logger.debug.msg('dd', offset=0.2)
    # logger.debug.msg('dd', widths=4,offset=0.2)


    # ------------------------------- subclass ------------------------------- #
    def child_func():
        logger.info.msg('aa')
    
    logger2 = Logger('tempppppppppppppp','head')
    logger2.set_clsname('parent')


    def parent_func():
        logger2.info.msg('bb')
        logger2.info.msg('bb',fname='myfunc!')
        logger2.set_sublogger(logger)
        child_func()

    parent_func()


    # --------------------------------- Task --------------------------------- #
    # task_logger = Logger(clsname='CLS', logname='task', context='sync')
    task_logger = Logger(clsname='CLS', logname='task', context='async')

    async def mytaskkkkkkkkkkkkkkkkkk():
        print(asyncio.current_task().get_name())
        task_logger.info.msg('hi')
    
    async def main():
        await mytaskkkkkkkkkkkkkkkkkk()


    asyncio.run(main())



