import logging
from typing import Literal
from Qrepeater.util import CustomLog
import inspect







class Msg(CustomLog):
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)


    def stream(self, status, *args):
        frame = f'{inspect.stack()[2].function}.{status}'
        header = f'/{frame:<20} ::: '
        body = ''.join([f"{arg:<12}, " for arg in args]) +" :::"
        self.msg(header + body) 