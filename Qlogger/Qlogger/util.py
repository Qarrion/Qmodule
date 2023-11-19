import os
import warnings
from typing import Literal
from configparser import ConfigParser, RawConfigParser

def read_config(
        filename, 
        parser:Literal['config','rawconfig']='config',
        location:Literal['file','project']='project', 
        ):
    """
    filename : <filename.ini>
    location : project -> project/config/

    >>> # 
    # filename fallback 
    conf = read_config(config, location='project')
    if conf is None:
        conf = read_config('default.ini',location='file')
        
    >>> # 
    # section fallback
    if name in conf.sections():
        conf_sect = conf[name]
    else:
        conf_sect = conf['default']
    """
    
    if location =='file':
        basedir = os.path.dirname(__file__)
    elif location =='project':
        basedir = os.path.join(os.getcwd(),'config')

    filepath = os.path.join(basedir, filename)

    # -------------------------------- isfile -------------------------------- #
    if not os.path.isfile(filepath):
        msg = f":::No {filename} file in 'project/config/':::"
        warnings.warn(msg)
        return None
    # ------------------------------------------------------------------------ #

    if parser == 'config':
        conf = ConfigParser()
    elif parser == 'rawconfig':
        conf = RawConfigParser()

    conf.read(filepath)

    # ------------------------------- isdefault ------------------------------ #
    if 'default' not in conf.sections():
        warnings.warn(":::No 'default' section:::")
    # ------------------------------------------------------------------------ #

    return conf

if __name__ == "__main__":
    config = read_config('test.ini')
    # config = read_config('myconfig.ini')
    # print(config['test']['var1'])
    # print(config.get('test','var1'))
   
    for s in  config.sections():
        print(s)