from typing import Literal
from Qlogger.config import Config
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
    def __init__(self, 
            name:str, 
            color:Literal['level','head','red','green','yellow','blue']='reset',
            file:str="log.ini", 
            debug=False
        ):
        """ 
        #### name : name is section of config /else/ default
        #### color : 'red','green','yellow','blue','purple','cyan','white'
        #### color : 'level', 'head', None
        #### config : project/config/<log.ini> /else/ defualt
        >>> #
        logger = Logger('test_fix', 'head', 'log.ini', debug=True)
        logger._dev_stream_handler_level('INFO')
        logger.debug('debug')
        logger.info('info')
        logger.warning('warn')
        logger.error('error')
        """
        super().__init__(name, level=logging.NOTSET)
    
        # ---------------------------- config file --------------------------- #    
        config = Config(inifile=file,fallback='default.ini',debug=debug)
        config.set_section(section=name)

        log_lev = config.section.get('level')
        log_fmt = config.section.get('fmt', raw=True)
        log_ymd = config.section.get('datefmt', raw=True, fallback=None)
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


if __name__ == "__main__":
    print('# ---------------------------------- fix --------------------------------- #')
    logging.basicConfig(level=logging.INFO)
    logger = Logger('test_fix', 'head', 'log.ini', debug=True)
    logger._dev_stream_handler_level('INFO')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warn')
    logger.error('error')
    # print('# --------------------------------- level -------------------------------- #')
    # logger = Logger('test_level', 'level', 'log.ini', True)
    # logger.info('info')
    # logger.debug('debug')
    # logger.warning('warn')
    # logger.error('error')
    # print('# --------------------------------- head --------------------------------- #')
    # logger = Logger('test_head', 'head', 'log.ini', True)
    # logger.info('info')
    # logger.debug('debug')
    # logger.warning('warn')
    # logger.error('error')
    