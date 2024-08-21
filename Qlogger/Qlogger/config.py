import os
from configparser import ConfigParser
from Qlogger.utils.custom_print import dprint
from typing import overload

class Config:
    """
    + os.path.join(os.path.dirname(__file__),fallback)
    + os.path.join(os.getcwd(),'config',filename)

    [default] : section fallback
    """
    def __init__(self,filename,fallback='default.ini',msg=False):
        self._msg = msg
        self._fallback = os.path.join(os.path.dirname(__file__),fallback)
        self._filename = os.path.join(os.getcwd(),'config',filename)

        self.parser = ConfigParser()

        if self.parser.read(self._filename):
            dprint(msg=f"inifile ('{self._filename}')", status=1, debug=self._msg)

        elif self.parser.read(self._fallback):
            dprint(msg=f"inifile ('{self._filename}')", status=0, debug=self._msg)
            dprint(msg=f"inifile ('{self._fallback}')", status=1, debug=self._msg)
        else:
            dprint(msg=f"inifile ('{self._filename}')", status=0, debug=self._msg)
            dprint(msg=f"inifile ('{self._fallback}')", status=0, debug=self._msg)

    def get(self, section, option, *, raw: bool = False, vars=None, fallback=None):
        if self.parser.has_section(section):
            dprint(f"section ('{section}')",1,self._msg)
            return self.parser.get(section, option, raw=raw, vars=vars, fallback=fallback)
        
        elif self.parser.has_section('default'):
            dprint(f"section ('{section}')",0,self._msg)
            dprint(f"section ('{'defualt'}')",1,self._msg)
            return self.parser.get('default', option, raw=raw, vars=vars, fallback=fallback)
        else:
            dprint(f"section ({'defualt'})",0,self._msg)
            
if __name__ == "__main__":
    config = Config('log.ini', msg=True)
    print(config.get(section='logger', option='level'))
    config.par
    config = Config('log2.ini', msg=True)
    print(config.get(section='logger', option='level'))
    print(config.get(section='logger', option='novar', fallback='no'))
