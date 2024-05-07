# https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
import asyncio
from http import client
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.tools.valider import Valider
from Qupbit.tools.parser import Parser
from typing import List, Literal
import requests, httpx
import logging


# from Qupbit.tools.tracer import Tracer 

"""
Quote-Base
KRW-BTC (원화마켓 Bitcoin)
"""

class Market:
    """ >>> # sync
    market = Market()
    rslt = market.get()
    cols = market.columns
    rows = market.to_rows(payload=rslt['payload'])
    
    >>> # asyncio
    async def main():
        async with market.xclient() as client:
            rslt = await market.xget(client)
            print(rslt['payload'][0])

    asyncio.run(main())
    """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    params = {"isDetails": 'true'}

    # columns = ['market','korean_name','english_name','market_warning','last_updated']
    
    def __init__(self, logger:logging.Logger=None):
        self.valider = Valider(logger)
        self.parser = Parser()
        self._custom = CustomLog(logger,'async')
        

    def get(self, session:requests.Session=None, key:Literal['status','header','payload','remain','text']=None, msg=False):
        """ >>> # return result
        result = market.get()
        result['status']
        result['header']
        result['payload']
        result['remain']
        result['text']
        # status, header, payload, remain[group, min, sec], text"""
        if session is None:
            resp = requests.get(url=self.url_market, headers=self.headers, params=self.params)
        else:
            resp = session.get(url=self.url_market, headers=self.headers, params=self.params)

        rslt = self.parser.response(resp)
        if msg : self._msg_result('get_market',rslt,"api") 
        if key is not None: rslt = rslt[key]
        return rslt
    
    async def xget(self, xclient:httpx.AsyncClient, key:Literal['status','header','payload','remain','text']=None, msg=False):
        """
        >>> # 
        async with market.xclient() as xclient:
            rslt = await market.xget(xclient)        
        """
        resp = await xclient.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self.parser.response(resp)
        if msg : self._msg_result('get_market',rslt,"xapi") 
        if key is not None: rslt = rslt[key]
        return rslt

    def xclient(self):
        """>>> return httpx.AsyncClient() """
        return httpx.AsyncClient()

    def to_rows(self,payload:List[dict], quote=None, base=None, market=None):
        """ >>> market.to_rows(result['payload']) 
        # market, korean_name, english_name, market_warning """
        selected_payload = self.parser.market(payload,'market', quote, base, market)
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
    
    def _msg_result(self, group, result:dict, frame:str):
        remain = result['remain']
        status = result['status']
        if status == 200:
            self._custom.debug.msg(group, remain['group']+"/g", f"{remain['min']}/m",f"{remain['sec']}/s",frame=frame)
        else:
            self._custom.error.msg(group, result['text'],frame=2)    

if __name__=='__main__':
    from Qupbit.utils.print_divider import eprint
    from Qupbit.utils.logger_color import ColorLog
    logger = ColorLog('upbit', 'green')
    
    market = Market(logger)

    # ---------------------------------- get --------------------------------- #
    eprint('get1')
    rslt = market.get()
    print(rslt)
    print(rslt.keys())
    eprint('payload')
    print(rslt['payload'][0:5])
    
    eprint('get2')
    rslt = market.get(None, 'payload')
    eprint('rows')
    rows = market.to_rows(payload=rslt)
    print(rows[0:5])

    # --------------------------------- async -------------------------------- #

    # async def main():
    #     async with market.xclient() as xclient:
    #         rslt = await market.xget(xclient)
    #         print(rslt['payload'][0])

    # asyncio.run(main())