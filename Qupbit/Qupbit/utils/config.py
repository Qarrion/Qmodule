import os
from typing import Literal
from configparser import ConfigParser, RawConfigParser

class Config:
    def __init__(self, filename, parser:Literal['config','rawconfig']='config', debug = False):
        self._filename = filename
        self._parser = parser
        self._debug = debug

        if parser == 'config':
            self.config = ConfigParser()
        elif parser == 'rawconfig':
            self.config = RawConfigParser()
    
    # ------------------------------ read config ----------------------------- #
    def read_proj(self, child_dir):
        """ child_dir : project/<child_dir>/"""                      
        filepath = os.path.join(os.getcwd(), child_dir, self._filename)
        return self._read_process(filepath,location='proj')

    def read_file(self, dunder_file):
        """+ dunder_file : __file__"""
        filepath = os.path.join(os.path.dirname(dunder_file), self._filename)
        return self._read_process(filepath,location='file') 
    
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
    if not config.read_proj('config'):
        if not config.read_file(__file__):
            pass

    if not config.is_section('test'):
        if not config.read_file(__file__):
            config.is_section('default')

