import logging
from typing import Literal
from Qupbit.utils.customlog import CustomLog










class Msg(CustomLog):
    
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def request(self, title, remain):
        self.stream(title, remain['group'], remain['min'], remain['sec'])