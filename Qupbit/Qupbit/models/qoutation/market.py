import requests
from Qupbit.tools.parser import Parser
from Qupbit.tools.tracer import Tracer 
from Qupbit.models import info
import logging
from typing import List

"""Quote-Base"""
"""
[{'market': 'KRW-BTC', 'korean_name': '비트코인', 'english_name': 'Bitcoin', 'market_warning': 'NONE', 
    'market_event': 
    {'warning': False, 
        'caution': {
        'PRICE_FLUCTUATIONS': False, 
        'TRADING_VOLUME_SOARING': False, 
        'DEPOSIT_AMOUNT_SOARING': False, 
        'GLOBAL_PRICE_DIFFERENCES': False, 
        'CONCENTRATION_OF_SMALL_ACCOUNTS': False
        }
    }
}]
"""
"""
['market','korean_name','english_name','warning',
'price_fluctuations',
'trading_volume_soaring',
'deposit_amount_soaring',
'global_price_differences',
'concentration_of_small_accounts']
"""

class Market:
    """ qoutation """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    params = {"isDetails": 'true'}

    cols_table = ['market','korean_name','english_name','warning',
        'price_fluctuations','trading_volume_soaring',
        'deposit_amount_soaring','global_price_differences',
        'concentration_of_small_accounts']

    def __init__(self, logger:logging.Logger=None, debug=True):
        self.tracer = Tracer(logger)
        self.parser = Parser()
        self._debug = debug

    def get(self):
        """status, header, payload, remain[group, min, sec], text"""
        resp = requests.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self.parser.response(resp)
        if self._debug : self.tracer.debug.request('market',rslt['remain']) 
        return rslt

    def test(self, rslt, header=True, column=True):
        if header:
            """group, remain 값 변동확인"""
            grp = info.qoutation['market']['group'] == rslt['remain']['group']
            sec = info.qoutation['market']['sec'] == rslt['remain']['sec']+1
            # if grp and sec:
            self.tracer.debug.test_header('market','group',rslt['remain']['group'],grp)
            self.tracer.debug.test_header('market','sec', rslt['remain']['sec']+1,sec)

        if column:
            """response.json 의 keys 변동확인"""
            rslt_keys = self.parser.response_allkeys(rslt['payload'][0])
            info_keys = info.qoutation['market']['columns']
            add = [r for  r in rslt_keys if r not in info_keys]
            rmv = [i for  i in info_keys if i not in rslt_keys]

            self.tracer.debug.test_column('market','added', add)
            self.tracer.debug.test_column('market','removed',rmv)

    def filter(self, payload:List[dict], qoute=None, base=None, market=None):
        rslt = self.parser.response_market(
            payload, 'market', qoute, base, market)
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
    from Qlogger import Logger
    logger = Logger('test','level')
    market = Market(logger)

    print('# ---------------------------------- get --------------------------------- #')
    rslt = market.get()
    print(rslt.keys())

    print('# --------------------------------- test --------------------------------- #')
    market.test(rslt,header=True, column=True)

    print('# -------------------------------- filter -------------------------------- #')
    rslt_filtered = market.filter(rslt['payload'], market='KRW-BTC')
    print("KRW-BTC", len(rslt_filtered))
    print(rslt_filtered)

    rslt_filtered = market.filter(rslt['payload'], qoute='KRW')
    print("qoute-KRW", len(rslt_filtered))

    rslt_filtered = market.filter(rslt['payload'], base='BTC')
    print("base-BTC", len(rslt_filtered))
    

    print('# --------------------------------- table -------------------------------- #')
    cols = market.to_cols(payload=rslt_filtered)
    rows = market.to_rows(payload=rslt_filtered)
    print(cols)
    print(rows)
    
