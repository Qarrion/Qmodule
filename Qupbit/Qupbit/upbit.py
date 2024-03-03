import logging
from Qupbit.models import Market


class Upbit:
    def __init__(self, logger:logging.Logger):
        self.market = Market(logger)

    def get_market(self, quote:str=None, base:str=None) -> list:
        resp = self.market.get()
        resp = self.market.filter(resp['payload'], quote, base)
        return [e['market'] for e in resp]

if __name__ == "__main__":
    from Qlogger import Logger

    lgger = Logger('upbit')
    upbit = Upbit(lgger)
    print(upbit.get_market(base='FLOW'))


