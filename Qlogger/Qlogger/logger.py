from Qlogger.util import Config
from typing import Literal
import threading
import contextvars
import logging

cmap = dict(
    reset = "\033[0m",
    red = "\033[31m",
    green = "\033[32m",
    yellow = "\033[33m",
    blue = "\033[34m",
    purple = "\033[35m",
    cyan = "\033[36m",
    white = "\033[37m")

level = {
    'WARNING':  cmap['yellow'],
    'INFO':     cmap['green'],
    'DEBUG':    cmap['blue'],
    'CRITICAL': cmap['red'],
    'ERROR':    cmap['red'],
    'RESET':    cmap['reset'],
}
class Logger(logging.Logger):

    # ------------------------------------------------------------------------ #
    def __init__(self, name:str, 
        color:Literal['level','red','green','yellow','blue']=None,
        config:str = "log.ini", debug=False):
        """
        #### name : name is section of config /else/ default
        #### color : 'red','green','yellow','blue','purple','cyan','white'
        #### color : 'level', None
        #### config : project/config/<log.ini> /else/ defualt
        """
        super().__init__(name, level=logging.NOTSET)
    
        # ---------------------------- config file --------------------------- #
        conf = Config(config,'rawconfig',debug)
        if conf.read_projdir(child_dir='config') is None:
            conf.read_libdir(fallback_file='default.ini')
        
        if conf.is_section(name) is None:
            conf.is_section('default')

        log_lev = conf.config.get(conf.section, 'level')
        log_fmt = conf.config.get(conf.section, 'fmt')
        log_ymd = conf.config.get(conf.section, 'datefmt', fallback=None)
        
        # ----------------------------- formatter ---------------------------- #
        if color == 'level':
            formatter = _LevelFormatter(fmt=log_fmt, datefmt=log_ymd)
        else:
            if color is None : color = 'reset'

            log_fmt_col = f"{cmap[color]}{log_fmt}{cmap['reset']}"
            formatter = logging.Formatter(fmt=log_fmt_col, datefmt=log_ymd)
    
        # -------------------------- stream_handler -------------------------- #
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_lev)

        if self.hasHandlers(): self.handlers.clear()        
        self.addHandler(stream_handler)  

class _LevelFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in level:
            levelname_color = level[levelname] + levelname + level['RESET']
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)

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
    logger = Logger('test_fix_logger', 'blue', 'log.ini', True)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')

    logger = Logger('test_lev_logger', 'level', 'log.ini', True)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')

    logger = Logger('test_chain', 'green', 'log.ini', False)
    chain = CustomLog(logger, 'async')
    chain.info.msg('info')
    chain.debug.msg('debug')
    chain.warning.msg('warning')
    chain.error.msg('error')

    class Log(CustomLog):
        def custom_msg(self, module, status, msg):
            header=f":: {module:<10} {status:<10}"
            self.msg(header + msg)

        def _module01_init(self):
            self.custom_msg('mod01', 'init', 'test_custom')

        def _module02_start(self):
            self.custom_msg('mod02', 'start', 'test_custom')
    

    mylogger = Log(logger, 'sync')
    mylogger.info._module01_init()
    mylogger.debug._module02_start()