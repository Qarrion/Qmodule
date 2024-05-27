import logging
from re import T
from turtle import up
from typing import Literal

import requests
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.models import Market, Candle
from Qupbit.tools.timez import Timez
import httpx
from datetime import datetime
""" only arg:session/client in get(sync) can be None """
class Upbit:
    def __init__(self, name:str='Upbit'):
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom  = CustomLog(logger,'async')
        self._custom.info.msg(name)
        self.market = Market(name)
        self.candle = Candle(name)
        self.timez = Timez()

    def xclient(self):
        """>>> return httpx.AsyncClient() """
        return httpx.AsyncClient()
    
    def session(self):
        """>>> return requests.Session() """
        return requests.Session()

    # ------------------------------------------------------------------------ #
    #                                   utils                                  #
    # ------------------------------------------------------------------------ #

    def uti_last(self, now_naive:datetime=None, rtype:Literal['kst','str']='str', msg=False):
        """>>> # return Last(time, stable, close, trade) '%Y-%m-%dT%H:%M:%S'
            if naive.second==0:
                naive_stable = naive.replace(second=1,microsecond=0)           
        """
        return self.candle.last_time(now_naive,rtype,msg=msg)

    def uti_kst(self, date_time_str:str):
        return self.candle._to_sql_kst(date_time_str=date_time_str)

    # ------------------------------------------------------------------------ #
    #                                  market                                  #
    # ------------------------------------------------------------------------ #
    def get_market(self, session:requests.Session=None, 
                   quote:Literal['KRW','BTC','USDT',None]=None, base:str=None, 
                   key:Literal['tuple','namedtuple']='tuple',msg=False) -> list:
        """+ response -> result -> payload -> to_rows"""
        payload = self.market.get(session=session,key='payload',msg=msg)
        filtered = self.market.parser.market(payload, 'market', quote=quote, base=base)
        rows = self.market.to_rows(payload=filtered,key=key)
        return rows

    async def xget_market(self, xclient:httpx.AsyncClient, 
                          quote:Literal['KRW','BTC','USDT',None]=None, base:str=None,
                          key:Literal['tuple','namedtuple']='tuple',msg=False) -> list:
        """+ response -> result -> payload -> to_rows"""
        payload = await self.market.xget(xclient=xclient,key='payload',msg=msg)
        filtered = self.market.parser.market(payload=payload, key='market', quote=quote, base=base)
        rows = self.market.to_rows(payload=filtered,key=key)
        return rows

    # ------------------------------------------------------------------------ #
    #                                  candle                                  #
    # ------------------------------------------------------------------------ #
    def get_candle(self,session:requests.Session=None,
                   market:str='KRW-BTC',to:str=None,count:int=200,
                   key:Literal['tuple','namedtuple']='tuple',msg=False):
        """+ response -> result -> payload -> to_rows"""
        payload = self.candle.get(session=session,market=market,to=to,count=count,
                                  tz='KST',key='payload',msg=msg)
        rows = self.candle.to_rows(payload=payload,key=key)
        return rows
    
    async def xget_candle(self, xclient:httpx.AsyncClient,
                          market:str='KRW-BTC',to:str=None,count:int=200,
                          key:Literal['tuple','namedtuple']='tuple',msg=False):
        """+ response -> result -> payload -> to_rows"""
        payload = await self.candle.xget(
            xclient=xclient,market=market,to=to,count=count,tz='KST',key='payload',msg=msg)
        rows = self.candle.to_rows(payload,key=key)
        # print(rows)
        return rows

    async def xget_candle_last(self, xclient:httpx.AsyncClient,
                          market:str='KRW-BTC',to:str=None,count:int=5,
                          key:Literal['tuple','namedtuple']='namedtuple',msg=False):
        """+ response -> result -> payload -> to_rows"""
        rslt = await self.candle.xget(
            xclient=xclient,market=market,to=to,count=count,tz='KST',msg=msg)
        rows = self.candle.to_rows(rslt['payload'],key=key)
        # print('server',rslt['time'])
        # print('traded',rows[0].time)

        return rows

if __name__ == "__main__":
    import asyncio
    upbit = Upbit()

    # ------------------------------------------------------------------------ #
    # rslt = upbit.get_market(quote='KRW')
    # print(rslt)

    # ------------------------------------------------------------------------ #
    # async def main():
    #     async with upbit.xclient() as xclient:
    #         rslt = await upbit.xget_market(xclient,'KRW')
    #     print(rslt)

    # asyncio.run(main())
    # ------------------------------------------------------------------------ #
    # rslt = upbit.get_candle(count=10)
    # print(rslt)

    # ------------------------------------------------------------------------ #
    async def main():
        async with upbit.xclient() as xclient:
            rslt = await upbit.xget_candle_last(xclient,count=10,msg=True)
        print(rslt)

    asyncio.run(main())
