import os
from typing import Literal
from configparser import ConfigParser

class Config:
    """
    >>> # ---------------------------- >>> config.ini ---------------------------- #
    # DEFAULT is common vars
    [DEFAULT]
    opt1 = 1
    opt2 = 2
    [default]
    # default is custom vars
    [section]
    # vars
    
    #
    >>> # --------------------------------- meth1 -------------------------------- #
    #! project/'config'/'test.ini',
    if not config.location_subdir('config'):
        #! path/to/execute/'test.ini',
        if not config.location_dirname(__file__):
            #! path/to/define/'config.ini',
            config.fallback('config.ini')
    
    #
    >>> # --------------------------------- meth2 -------------------------------- #
    config.location_subdir('conifg',config_fallback='test.ini')
    config.location_dirname(__file__,config_fallback='test.ini')
    config.section_fallback('section','default')

    #
    >>> # -------------------------------- example ------------------------------- #
    config.data.get('section', 'option', fallback='val')
    config.get('option', raw=True, fallback='val')
    """

    def __init__(self, config_filename, debug = False):
        self._filename = config_filename
        self._debug = debug
        self.section = None 
        self.data = ConfigParser()

    # ------------------------------ read config ----------------------------- #
    def read_config_subdir(self, folder_name:str, config_fallback:str=None):
        """+ folder_name : project sub folder
        * project/<folder_name>/ **filename**"""                      
        filepath = os.path.join(os.getcwd(), folder_name, self._filename)
        
        rint = self._data_read(filepath, location='subdir')
        if config_fallback is not None and rint == 0:            
            rint = self._read_config_fallback(config_fallback)
        return rint

    def read_config_dirname(self, file_name:str, config_fallback:str=None):
        """+ file_name : os.path.dirname(file_name)
        + path/to/execute/ **filename** (when dirname = __file__)"""
        filepath = os.path.join(os.path.dirname(file_name), self._filename)
    
        rint = self._data_read(filepath,location='dirname')
        if config_fallback is not None and rint == 0:            
            rint = self._read_config_fallback(config_fallback)
        return rint

    def _read_config_fallback(self, filename):
        """+ filename : override filename
        + path/to/define/ **override**
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        return self._data_read(filepath,location='fallback') 

    # ----------------------------- read section ----------------------------- #
    def read_section(self, section_name:str, fallback_name:str=None):
        if section_name in self.data.sections(): 
            self.section = section_name
            self._debug_print(f'0 ->> section ({section_name}) in target','green')
            return 1
        else:
            self._debug_print(f'1 ->> section ({section_name}) not in config ({self._filename})','red')
            if fallback_name is not None:
                if fallback_name in self.data.sections(): 
                    self._debug_print(f'0 ->> section ({fallback_name}) in fallback','green')
                    self.section = fallback_name
                    return 1
                else:
                    self._debug_print(f'1 ->> section ({fallback_name}) not in config ({self._filename})','red')
                    return 0
            else:
                return 0

    # ---------------------------------- get --------------------------------- #
    def get(self, option, raw=False, fallback=None):
        return self.data.get(self.section, option=option, raw=raw, fallback=fallback)
    # --------------------------------- debug -------------------------------- #
    def debug_sections(self):
        print(f'config ({self._filename}), sections ({self.data.sections()})')

    def debug_options(self, section):
        print(f'config ({self._filename}), section ({section}),  options ({self.data.options(section)})')

    # --------------------------------- other -------------------------------- #
    
    def _data_read(self, filepath, location=None):
        relapath = os.path.join(r'.', os.path.relpath(filepath, os.getcwd()))
        
        if os.path.isfile(filepath):
            self.data.read(filepath)
            self._debug_print(f'1 ->> config ({self._filename}) in {location} ({relapath}) with sections ({self.data.sections()})' , 'green')
            return 1
        else:
            self._debug_print(f'0 ->> config ({self._filename}) not in {location} ({relapath})', 'red')
            return 0    

    def _debug_print(self, msg, color):
        if color == 'red': self._debug = True
        if self._debug: self._color_msg(msg, color)

    def _color_msg(self, msg, color:Literal['red','green']):
        name, shell = ['green', 'red', 'reset'], ["\033[32m", "\033[31m", "\033[0m"]
        cmap = dict(zip(name, shell))
        print(f"{cmap[color]}{msg}{cmap['reset']}")

if __name__ == "__main__":
    config = Config(config_filename='test.ini', debug=True)

    # --------------------------------- meth1 -------------------------------- #
    # #! project/'config'/'test.ini',
    # if not config.read_config_subdir('config'):
    #     #! path/to/execute/'test.ini',
    #     if not config.read_config_dirname(__file__):
    #         #! path/to/define/'config.ini',
    #         # config.fallback('config.ini')
    #         pass

    # --------------------------------- meth2 -------------------------------- #
    config.read_config_subdir('conifg',config_fallback='test.ini')
    config.read_config_dirname(__file__,config_fallback='test.ini')
    config.read_section('section','default')

    # --------------------------------- final -------------------------------- #
    config.debug_options('section')
    #? get options in section

    print(config.data.get('section','level2', fallback='no_value'))

    #? searches for option('level2') in section('section')
    #? not founded, looks for option('level2') in section('DEFAULT')
    #? not founded, return fallback('no_value')


    # -------------------------------- example ------------------------------- #
    config.data.get('section', 'option', fallback='val')
    config.get('option', raw=True, fallback='val')