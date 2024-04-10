# https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.tools.valider import Valider
from Qupbit.tools.parser import Parser
from typing import List
import requests
import logging
# from Qupbit.tools.tracer import Tracer 

"""
Quote-Base
KRW-BTC (원화마켓 Bitcoin)
"""

class Market:
    """ >>> #
    market = Market()
    rslt = market.get()
    cols = market.columns
    rows = market.to_rows(payload=rslt['payload'])
    """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    columns = ['market','korean_name','english_name','market_warning','last_updated']

    def __init__(self, logger:logging.Logger=None, debug=True):
        self.custom = CustomLog(logger,'async')
        self.valider = Valider(logger)
        self.parser = Parser()
        self._debug = debug

    def _req_get(self):
        params = {"isDetails": 'true'}
        resp = requests.get(url=self.url_market, headers=self.headers, params=params)
        return resp

    def get(self):
        """ >>> # return result
        result = market.get()
        result['status']
        result['header']
        result['payload']
        result['remain']
        result['text']
        # status, header, payload, remain[group, min, sec], text"""
        
        resp = self._req_get()
        rslt = self.parser.response(resp)
        if self._debug : self._msg_result('market',rslt) 
        return rslt
    
    def to_rows(self,payload:List[dict], qoute=None, base=None, market=None):
        """ >>> market.to_rows(result['payload']) 
        # [row for row in payload] """
        selected_payload = self.parser.market(payload,'market', qoute, base, market)
        selected_rows =[
            (
                d['market'], d['korean_name'],d['english_name'],
                d['market_event']['warning'],
                # d['market_event']['caution']['PRICE_FLUCTUATIONS'],
                # d['market_event']['caution']['TRADING_VOLUME_SOARING'],
                # d['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
                # d['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
                # d['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
            ) 
                for d in selected_payload
        ]
        return selected_rows
    
    def _msg_result(self,group, result:dict):
        remain = result['remain']
        status = result['status']
        if status == 200:
            self.custom.debug.msg(group, remain['group']+"/g", f"{remain['min']}/m",f"{remain['sec']}/s",back=2)
        else:
            self.custom.error.msg(group, result['text'],back=2)    

if __name__=='__main__':
    from Qupbit.utils.print_divider import eprint
    from Qupbit.utils.logger_color import ColorLog

    logger = ColorLog('test','green')
    market = Market(logger)

    # --------------------------------- valid -------------------------------- #
    eprint('valid')
    
    # ---------------------------------- get --------------------------------- #
    eprint('get')
    rslt = market.get()
    # print(rslt['payload'])
    # ------------------------------------------------------------------------ #
    eprint('rslt')
    print(rslt.keys())
    eprint('payload')
    print( rslt['payload'][0:5])
    # # ------------------------------------------------------------------------ #
    cols = market.columns
    rows = market.to_rows(payload=rslt['payload'])
    eprint('cols')
    print(cols)
    eprint('rows')
    print(rows[0:5])


