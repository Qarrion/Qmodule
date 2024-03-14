# https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
import requests
import logging
from Qupbit.tools.parser import Parser
from Qupbit.tools.tracer import Tracer 
from Qupbit.tools.valider import Valider
from typing import List

"""Quote-Base"""

class Market:
    """ qoutation """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    columns = ['market','korean_name','english_name','market_warning','last_updated']

    def __init__(self, logger:logging.Logger=None, debug=True):
        self.tracer = Tracer(logger)
        self.valider = Valider(logger)
        self.parser = Parser()
        self._debug = debug

    def requests_get(self):
        params = {"isDetails": 'true'}
        resp = requests.get(url=self.url_market, headers=self.headers, params=params)
        return resp

    def get(self):
        """
        + retun dict
        + keys (status, header, payload, remain[group, min, sec], text)
        + if (status = 200) debug else error 
        """
        resp = self.requests_get()
        rslt = self.parser.response(resp)
        if self._debug : self.tracer.request('market',rslt) 
        return rslt
    
    def valid(self):
        rlst = self.get()
        self.valider.check('market',rlst)

    def to_rows(self,payload:List[dict]):
        rows =[
            (
                d['market'], d['korean_name'],d['english_name'],
                d['market_event']['warning'],
                # d['market_event']['caution']['PRICE_FLUCTUATIONS'],
                # d['market_event']['caution']['TRADING_VOLUME_SOARING'],
                # d['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
                # d['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
                # d['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
            ) 
                for d in payload
        ]
        return rows
    
if __name__=='__main__':
    from Qupbit.utils.print_divider import eprint
    from Qlogger import Logger

    logger = Logger('test','level')
    market = Market(logger)

    # --------------------------------- valid -------------------------------- #
    eprint('valid')
    
    # ---------------------------------- get --------------------------------- #
    eprint('get')
    rslt = market.get()
    rslt['payload']
    # ------------------------------------------------------------------------ #
    eprint('rslt')
    print(rslt.keys())
    eprint('payload')
    print( rslt['payload'][0:5])
    # ------------------------------------------------------------------------ #
    cols = market.columns
    rows = market.to_rows(payload=rslt['payload'])
    eprint('cols')
    print(cols)
    eprint('rows')
    print(rows[0:5])
