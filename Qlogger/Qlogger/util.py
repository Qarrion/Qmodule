import os
from typing import Literal
from configparser import ConfigParser, RawConfigParser

class Config:

    """
    >>> # Config : Config Builder
    config = Config(filename='test.ini', debug=True)
    # project/'config'/'test.ini',
    if not config.file_in_folder('config'):
        # path/to/execute/'test.ini',
        if not config.file_in_dirname(__file__):
            # path/to/define/'config.ini',
            config.fallback('config.ini')

    >>> config.data.get()
    """
    def __init__(self, filename, parser:Literal['config','rawconfig']='config', debug = False):
        self._filename = filename
        self._parser = parser
        self._debug = debug

        if parser == 'config':
            self.data = ConfigParser()
        elif parser == 'rawconfig':
            self.data = RawConfigParser()
    
    # ------------------------------ read config ----------------------------- #
    def file_in_folder(self, folder_name):
        """+ folder_name : project sub folder
        * project/<folder_name>/ **filename**"""                      
        filepath = os.path.join(os.getcwd(), folder_name, self._filename)
        return self._read_process(filepath,location='folder')

    def file_in_dirname(self, file_name):
        """+ file_name : os.path.dirname(file_name)
        + path/to/execute/ **filename** (when dirname = __file__)"""
        filepath = os.path.join(os.path.dirname(file_name), self._filename)
        return self._read_process(filepath,location='file') 
    
    def fallback(self, filename):
        """+ filename : override filename
        + path/to/define/ **override**
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        return self._read_process(filepath,location='fallback') 

    def options(self, section):
        print(f'config ({self._filename}), section ({section}),  options ({self.data.options(section)})')

    # --------------------------------- other -------------------------------- #
    def _read_process(self, filepath, location=None):
        relapath = os.path.relpath(filepath, os.getcwd())
        if os.path.isfile(filepath):
            self.data.read(filepath)
            self._debug_process(f'1 ->> config exists in {location} (.\{relapath}) with sections {self.data.sections()}' , 'green')
            return 1
        else:
            self._debug_process(f'0 ->> config not exists in {location} ({filepath})', 'red')
            return 0    

    def _debug_process(self, msg, color):
        if color == 'red':
            self._debug = True

        if self._debug:
            self._color_print(msg, color)

    def _color_print(self, msg, color:Literal['red','green']):
        name = ['green', 'red', 'reset']
        shell = ["\033[32m", "\033[31m", "\033[0m"]
        cmap = dict(zip(name, shell))
        print(f"{cmap[color]}{msg}{cmap['reset']}")

if __name__ == "__main__":
    config = Config(filename='test.ini', debug=True)
    #! project/'config'/'test.ini',
    if not config.file_in_folder('config'):
        #! path/to/execute/'test.ini',
        if not config.file_in_dirname(__file__):
            #! path/to/define/'config.ini',
            config.fallback('config.ini')

    config.options('section')
    #? get options in section

    print(config.data.get('section','level2', fallback='no_value'))

    #? searches for option('level2') in section('section')
    #? not founded, looks for option('level2') in section(DEFAULT)
    #? not founded, return fallback('no_value')


# import os
# from typing import Literal
# from configparser import ConfigParser, RawConfigParser

# class Config:
#     def __init__(self, filename, parser:Literal['config','rawconfig']='config', debug = False):
#         self._filename = filename
#         self._parser = parser
#         self._debug = debug
#         if parser == 'config':
#             self.config = ConfigParser()
#         elif parser == 'rawconfig':
#             self.config = RawConfigParser()
    
#     def _read_process(self, filepath, debug=None):
#         # rela_path = os.path.relpath(filepath, os.getcwd())
#         if os.path.isfile(filepath):
#             self.config.read(filepath)
#             self._debug_process(f'config_{debug} ({filepath})', 'done')
#             return self.config
#         else:
#             self._debug_process(f'config_{debug} ({filepath})', 'fail')
#             return None    

#     def _debug_process(self, msg, status:Literal['done', 'fail']):
#         green = "\033[32m"
#         red = "\033[31m"
#         reset = "\033[0m"
#         if self._debug:
#             if status=='done':
#                 print(f"{green}->> Done {msg} {reset}")
#             elif status =='fail':
#                 print(f"{red}->> Fail {msg} {reset}")

#     def read_projdir(self, child_dir):
#         """+ child_dir : project/<child_dir>/"""                      
#         filepath = os.path.join(os.getcwd(), child_dir, self._filename)
#         return self._read_process(filepath,'project')

#     def read_filedir(self, dunder_file):
#         """+ dunder_file : __file__"""
#         filepath = os.path.join(os.path.dirname(dunder_file), self._filename)
#         return self._read_process(filepath,'filedir') 
        
#     def read_libdir(self, fallback_file='default.ini'):
#         """+ fallback_file : default fallback file"""
#         filepath = os.path.join(os.path.dirname(__file__), fallback_file)
#         return self._read_process(filepath,'libdir')
    
#     def is_section(self, section):
#         if section not in self.config.sections():
#             self.section = None
#             self._debug_process(f'section ({section})', 'fail')
#             return None
#         else :
#             self.section = section
#             self.item = self.config.options(section)
#             self._debug_process(f'section ({section}) item {self.item}', 'done')
#             return section

# if __name__ == "__main__":
#     config = Config(filename='nofile.ini', debug=True)
#     if config.read_projdir(child_dir='config') is None :
#         if config.read_filedir(dunder_file=__file__) is None:
#             config.read_libdir(fallback_file='default.ini')
#     if config.is_section('test') is None:
#         config.is_section('default')
#         print(config.config.get('default', 'level'))