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

cmap_hint = Literal['reset','red','green','yellow','blue','purple','cyan','white']

class Logger(logging.Logger):

    # ------------------------------------------------------------------------ #
    def __init__(self, name:str, 
        color:Literal['red','green','yellow','blue']=None,
        config:str = "log.ini", warning=False):
        """
        #### name : name is section of config /else/ default
        #### color : 'red','green','yellow','blue','purple','cyan','white'
        #### config : project/config/<log.ini> /else/ defualt
        """
        super().__init__(name, level=logging.NOTSET)
    
        # ---------------------------- config file --------------------------- #
        conf = Config(config,'rawconfig',warning)
        if conf.read_projdir(child_dir='config') is None:
            conf.read_libdir(fallback_file='default.ini')
        
        if conf.is_section(name) is None:
            conf.is_section('default')

        log_lev = conf.config.get(conf.section, 'level')
        log_fmt = conf.config.get(conf.section, 'fmt')
        log_ymd = conf.config.get(conf.section, 'datefmt', fallback=None)
        
        # ----------------------------- formatter ---------------------------- #
        if color is None : color = 'reset'

        log_col = f"{cmap[color]}{log_fmt}{cmap['reset']}"
        formatter = logging.Formatter(fmt=log_col, datefmt=log_ymd)
    
        # -------------------------- stream_handler -------------------------- #
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_lev)

        if self.hasHandlers(): self.handlers.clear()        
        self.addHandler(stream_handler)  


class Chain:
    def __init__(self, logger:logging.Logger,
                 execution:Literal['sync', 'thread', 'async'] = 'sync'):
        self.logger = logger
        if execution == 'sync':
            self.method = _Sync()
        elif execution =='thread':
            self.method = _Thread()
        elif execution == 'async':
            self.method = _Async()
    
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
    logger = Logger('test', 'blue', 'log.ini', False)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')

    chain = Chain(logger, execution='sync')
    chain.info.log('test')
    chain.debug.log('debug')
    chain.warning.log('warn')
    chain.error.log('error')


    