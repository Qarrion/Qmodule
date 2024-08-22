from Qlogger import Logger
from Qupbit.tools.parser import Parser
from typing import List, Literal
import requests
import httpx
import asyncio
from collections import namedtuple

Row = namedtuple('Row',['market','korean_name','english_name','market_warning','note'])

class Market:
    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    params = {"isDetails": 'true'}

    def __init__(self, name = 'market'):
        self._logger = Logger(name,clsname='Market',msg=False)
        self._parser = Parser()
        self._row = Row

    def get(self, payload = True, 
            quote:Literal['KRW','BTC','USDT']=None, base =None, 
            msg=False):
        """ + base : coin ticker
        + quote : 'KRW' or 'BTC' or 'USDT'
        + payload : return only payload
        + else : result['status','header','payload','remain','text']
        """
        # ----------------------------- requests ----------------------------- #
        resp = requests.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self._parser.response(resp)
        rslt['payload'] = self._parser.market(rslt['payload'], key='market', base=base, quote=quote)
        # ----------------------------- exception ---------------------------- #
        if rslt['status'] == 200:
            if msg : self._logger.info.msg(f'{base=:}', f'{quote=:}',rslt['remain'])

        elif rslt['status'] == 429:
            self._logger.error.msg(f'{base=:}',f'{quote=:}', f"code({rslt['status']})", 'too_many_requests!')    

        else:
            self._logger.error.msg(f'{base=:}',f'{quote=:}', f"code({rslt['status']})", rslt['text'])  
        # ------------------------------ return ------------------------------ #
        resp.raise_for_status()
        if payload: rslt = rslt['payload']
        return rslt

    async def xget(self, xclient:httpx.AsyncClient, payload = True, 
            quote:Literal['KRW','BTC','USDT']=None, base =None, 
            msg=False):
        """
        >>> # 
        async with market.xclient() as xclient:
            rslt = await market.xget(xclient)
        """
        # ----------------------------- requests ----------------------------- #
        resp = await xclient.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self._parser.response(resp)
        rslt['payload'] = self._parser.market(rslt['payload'], key='market', base=base, quote=quote)
        # ----------------------------- exception ---------------------------- #
        if rslt['status'] == 200:
            if msg : self._logger.info.msg(f'{base=:}', f'{quote=:}',rslt['remain'])

        elif rslt['status'] == 429:
            self._logger.error.msg(f'{base=:}',f'{quote=:}', f"code({rslt['status']})", 'too_many_requests!')    

        else:
            self._logger.error.msg(f'{base=:}',f'{quote=:}', f"code({rslt['status']})", rslt['text'])   
        # ------------------------------ return ------------------------------ #
        resp.raise_for_status()
        if payload: rslt = rslt['payload']
        return rslt
    
    def to_rows(self, payload, quote=None, base=None, market=None):
        """ >>> market.to_rows(result['payload']) 
        # market, korean_name, english_name, market_warning """
        selected_payload = self._parser.market(payload,'market', quote, base, market)
        selected_rows =[
            Row(
                d['market'], d['korean_name'], d['english_name'],
                d['market_event']['warning'],
                'fetch'
            ) 
                for d in selected_payload
        ]
        return selected_rows

    def to_dict(self, row:Row):
        if isinstance(row, Row):
            return row._asdict()
        else:
            print(f"\033[31m row is not instance Row({Row.index} \033[0m")

if __name__ =="__main__":
    market = Market()
    rslt = market.get(msg=True, payload=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    rslt = market.get(msg=True)
    # # print(rslt)
    async def main():
        async with httpx.AsyncClient() as xclient:
            rslt = await market.xget(xclient,quote='KRW', payload=True, msg=True)
            rslt = await market.xget(xclient,base='ETH', payload=True, msg=True)
            print(rslt)

            rows = market.to_rows(rslt)
            print(rows)

    asyncio.run(main())