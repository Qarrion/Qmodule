from Qlogger.util import Config
from typing import Literal
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
            color:Literal['level','head','red','green','yellow','blue']=None,
            config:str="log.ini", 
            debug=False
        ):
        """
        #### name : name is section of config /else/ default
        #### color : 'red','green','yellow','blue','purple','cyan','white'
        #### color : 'level', 'head', None
        #### config : project/config/<log.ini> /else/ defualt
        """
        super().__init__(name, level=logging.NOTSET)
    
        # ---------------------------- config file --------------------------- #
        conf = Config(config_filename=config, debug=debug)
        conf.read_config_subdir(folder_name='config',config_fallback='default.ini')
        conf.read_section(section_name=name, fallback_name='logger')

        log_lev = conf.data.get(conf.section, 'level')
        log_fmt = conf.data.get(conf.section, 'fmt', raw=True)
        log_ymd = conf.data.get(conf.section, 'datefmt', raw=True, fallback=None)
        
        # ----------------------------- formatter ---------------------------- #
        if color == 'level':
            formatter = LevelFormatter(fmt=log_fmt, datefmt=log_ymd)
        elif color == 'head':
            formatter = HeadFormatter(fmt=log_fmt, datefmt=log_ymd)
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
    logger = Logger('test_fix', 'blue', 'log.ini', True)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')
    print('# --------------------------------- level -------------------------------- #')
    logger = Logger('test_level', 'level', 'log.ini', True)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')
    print('# --------------------------------- head --------------------------------- #')
    logger = Logger('test_head', 'head', 'log.ini', True)
    logger.info('info')
    logger.debug('debug')
    logger.warning('warn')
    logger.error('error')
    