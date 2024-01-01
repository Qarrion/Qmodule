import logging
from Qupbit.api import market


class Upbit:
    def __init__(self, logger:logging.Logger):
        self.logger = logger

def get_market(quote:str=None, base:str=None):
    resp = market.get()
    resp = market.filter(resp['payload'], quote, base)
    return [e['market'] for e in resp]


