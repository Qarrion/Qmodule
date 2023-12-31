import os
from typing import Literal
from configparser import ConfigParser, RawConfigParser

class Config:
    def __init__(self, filename, parser:Literal['config','rawconfig']='config', debug = False):
        self._filename = filename
        self._parser = parser
        self._debug = debug
        self._config = None

        if parser == 'config':
            self.config = ConfigParser()
        elif parser == 'rawconfig':
            self.config = RawConfigParser()
    
    # ------------------------------ read config ----------------------------- #
    def read_project(self, child_dir):
        """+ child_dir : subfolder
        * project/<child_dir>/**filename**"""                      
        filepath = os.path.join(os.getcwd(), child_dir, self._filename)
        return self._read_process(filepath,location='project')

    def read_execute(self, dunder_file):
        """+ dunder_file : __file__
        * path/to/execute/**filename**"""
        filepath = os.path.join(os.path.dirname(dunder_file), self._filename)
        return self._read_process(filepath,location='execute') 
    
    def read_written(self, fallback_file):
        """+ fallback_file : default fallback file"""
        filepath = os.path.join(os.path.dirname(__file__), fallback_file)
        return self._read_process(filepath,'written')

    # ----------------------------- read section ----------------------------- #
    def is_section(self, section):
        if section not in self.config.sections():
            self._debug_process(f'0 section ({section}) not in config', 'red')
            return 0
        else :
            self._debug_process(
                f'1 section ({section}) items {self.config.options(section)}', 'green')
            return section

    # --------------------------------- other -------------------------------- #
    def _read_process(self, filepath, location=None):
        # relapath = os.path.relpath(filepath, os.getcwd())
        if os.path.isfile(filepath):
            self._debug_process(f'1 config {location} in (.\{filepath})' , 'green')
            self.config.read(filepath)
            return 1
        else:
            self._debug_process(f'0 config {location} not in (.\{filepath})', 'red')
            return 0    

    def _debug_process(self, msg, color):
        if self._debug:
            self._color_print(msg, color)

    def _color_print(self, msg, color:Literal['red','green']):
        name = ['green', 'red', 'reset']
        shell = "\033[32m", "\033[31m", "\033[0m"
        cmap = dict(zip(name, shell))
        print(f"{cmap[color]}{msg}{cmap['reset']}")
        if shell=='green':
            print(f"{cmap[color]}{msg}{cmap['reset']}")
        elif shell =='red':
            print(f"{cmap[color]}{msg}{cmap['reset']}")

if __name__ == "__main__":
    config = Config(filename='limit.ini', debug=True)
    if not config.read_project('config'):
        if not config.read_execute(__file__):
            if not config.read_written('default.ini'):  
                pass

    if not config.is_section('test'):
        pass
