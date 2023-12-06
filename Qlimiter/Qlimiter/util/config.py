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
    
    def _read_process(self, filepath, debug=None):
        # rela_path = os.path.relpath(filepath, os.getcwd())
        if os.path.isfile(filepath):
            self.config.read(filepath)
            self._debug_process(f'config_{debug} ({filepath})', 'done')
            return self.config
        else:
            self._debug_process(f'config_{debug} ({filepath})', 'fail')
            return None    

    def _debug_process(self, msg, status:Literal['done', 'fail']):
        green = "\033[32m"
        red = "\033[31m"
        reset = "\033[0m"
        if self._debug:
            if status=='done':
                print(f"{green}->> Done {msg} {reset}")
            elif status =='fail':
                print(f"{red}->> Fail {msg} {reset}")

    def read_projdir(self, child_dir):
        """+ child_dir : project/<child_dir>/"""                      
        filepath = os.path.join(os.getcwd(), child_dir, self._filename)
        return self._read_process(filepath,'project')

    def read_filedir(self, dunder_file):
        """+ dunder_file : __file__"""
        filepath = os.path.join(os.path.dirname(dunder_file), self._filename)
        return self._read_process(filepath,'filedir') 
        
    def read_libdir(self, fallback_file='default.ini'):
        """+ fallback_file : default fallback file"""
        filepath = os.path.join(os.path.dirname(__file__), fallback_file)
        return self._read_process(filepath,'libdir')
    
    def is_section(self, section):
        if section not in self.config.sections():
            self.section = None
            self._debug_process(f'section ({section})', 'fail')
            return None
        else :
            self.section = section
            self.item = self.config.options(section)
            self._debug_process(f'section ({section}) item {self.item}', 'done')
            return section

if __name__ == "__main__":
    config = Config(filename='nofile.ini', debug=True)
    if config.read_projdir(child_dir='config') is None :
        if config.read_filedir(dunder_file=__file__) is None:
            config.read_libdir(fallback_file='default.ini')
    if config.is_section('test') is None:
        config.is_section('default')
        print(config.config.get('default', 'level'))