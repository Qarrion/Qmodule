# https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
import requests
import logging
from Qupbit.tools.parser import Parser
from Qupbit.tools.tracer import Tracer 
from typing import List

"""Quote-Base"""

class Market:
    """ qoutation """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
   
    cols_table = ['market','korean_name','english_name','warning',
        'price_fluctuations','trading_volume_soaring',
        'deposit_amount_soaring','global_price_differences',
        'concentration_of_small_accounts']

    def __init__(self, logger:logging.Logger=None, debug=True):
        self.tracer = Tracer(logger)
        self.parser = Parser()
        self._debug = debug

    def requests_get(self):
        params = {"isDetails": 'true'}
        resp = requests.get(url=self.url_market, headers=self.headers, params=params)
        return resp

    def get(self):
        """status, header, payload, remain[group, min, sec], text"""
        resp = self.requests_get()
        rslt = self.parser.response(resp)
        if self._debug : self.tracer.request('market',rslt) 
        return rslt
    
    def to_cols(self, payload:List[dict]):
        keys_response = self.parser.response_allkeys(payload[0])
        keys_lower = [k.lower() for k in keys_response]

        cols_not_in_keys = [col.lower() for col in self.cols_table if col.lower() not in keys_lower]
        if cols_not_in_keys:
            if self._debug :  self.tracer.warning.cols_match('market',cols_not_in_keys)
        return self.cols_table

    def to_rows(self,payload:List[dict]):
        rows =[
            (
                d['market'], d['korean_name'],d['english_name'],
                d['market_event']['warning'],
                d['market_event']['caution']['PRICE_FLUCTUATIONS'],
                d['market_event']['caution']['TRADING_VOLUME_SOARING'],
                d['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
                d['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
                d['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
            ) 
                for d in payload
        ]
        return rows
    
if __name__=='__main__':
    from Qupbit.utils.print_divider import eprint
    from Qlogger import Logger

    logger = Logger('test','level')
    market = Market(logger)

    # ------------------------------------------------------------------------ #
    eprint('get')
    rslt = market.get()
    rslt['payload']
    # ------------------------------------------------------------------------ #
    eprint('rslt')
    print(rslt.keys())
    eprint('payload')
    print( rslt['payload'][0:5])
    # ------------------------------------------------------------------------ #
    cols = market.to_cols(payload=rslt['payload'])
    rows = market.to_rows(payload=rslt['payload'])
    eprint('cols')
    print(cols)
    eprint('rows')
    print(rows[0:5])


    # print('# --------------------------------- test --------------------------------- #')
    # market.test(rslt, header=True, column=True)

    # print('# -------------------------------- filter -------------------------------- #')
    # rslt_filtered = market.filter(rslt['payload'], market='KRW-BTC')
    # print("KRW-BTC", len(rslt_filtered))
    # print(rslt_filtered)

    # rslt_filtered = market.filter(rslt['payload'], qoute='KRW')
    # print("qoute-KRW", len(rslt_filtered))

    # rslt_filtered = market.filter(rslt['payload'], base='BTC')
    # print("base-BTC", len(rslt_filtered))
    
