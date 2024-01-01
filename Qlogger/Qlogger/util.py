import os
from typing import Literal
from configparser import ConfigParser, RawConfigParser

class Config:

    def __init__(self, config_filename, parser:Literal['config','rawconfig']='config', debug = False):
        self._filename = config_filename
        self._debug = debug

        if parser == 'config':
            self.data = ConfigParser()
        elif parser == 'rawconfig':
            self.data = RawConfigParser()

    def data_read(self, filepath, location=None):
        # relapath = os.path.join(r'.', os.path.relpath(filepath, os.getcwd())) if self._debug else filepath
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

    # ------------------------------ read config ----------------------------- #
    def location_subdir(self, folder_name:str, config_fallback:str=None):
        """+ folder_name : project sub folder
        * project/<folder_name>/ **filename**"""                      
        filepath = os.path.join(os.getcwd(), folder_name, self._filename)
        
        rint = self.data_read(filepath,location='subdir')
        if config_fallback is not None and rint == 0:            
            rint = self.fallback(config_fallback)
        return rint

    def location_dirname(self, file_name:str, config_fallback:str=None):
        """+ file_name : os.path.dirname(file_name)
        + path/to/execute/ **filename** (when dirname = __file__)"""
        filepath = os.path.join(os.path.dirname(file_name), self._filename)
    
        rint = self.data_read(filepath,location='dirname')
        if config_fallback is not None and rint == 0:            
            rint = self.fallback(config_fallback)
        return rint

    def fallback(self, filename):
        """+ filename : override filename
        + path/to/define/ **override**
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        return self.data_read(filepath,location='fallback') 

    def debug_sections(self):
        print(f'config ({self._filename}), sections ({self.data.sections()})')
        
    def debug_options(self, section):
        print(f'config ({self._filename}), section ({section}),  options ({self.data.options(section)})')

    # --------------------------------- other -------------------------------- #


if __name__ == "__main__":
    config = Config(config_filename='test.ini', debug=True)

    # --------------------------------- meth1 -------------------------------- #
    # #! project/'config'/'test.ini',
    # if not config.location_subdir('config'):
    #     #! path/to/execute/'test.ini',
    #     if not config.location_dirname(__file__):
    #         #! path/to/define/'config.ini',
    #         config.fallback('config.ini')

    # --------------------------------- meth2 -------------------------------- #
    # config.location_subdir('conifg',config_fallback='test.ini')
    config.location_dirname(__file__,config_fallback='test.ini')



    # --------------------------------- final -------------------------------- #
    config.debug_options('section')
    # #? get options in section

    print(config.data.get('section','level2', fallback='no_value'))

    #? searches for option('level2') in section('section')
    #? not founded, looks for option('level2') in section('DEFAULT')
    #? not founded, return fallback('no_value')
