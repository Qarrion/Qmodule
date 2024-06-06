import logging
from math import e
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
    def __init__(self, name:str='upbit',msg=True):
        CLSNAME = 'Upbit'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger, CLSNAME,'async')
        if msg : self._custom.info.msg(name)

        self.market = Market(name,msg=False)
        self.candle = Candle(name,msg=False)
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
        return self.candle.chk_time(now_naive,rtype,msg=msg)

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
                market:str='KRW-BTC',count:int=5, key:Literal['tuple','namedtuple']='namedtuple',msg=False):
        """+ response -> result -> payload -> to_rows"""
        rslt = await self.candle.xget(
            xclient=xclient,market=market,to=None,count=count,msg=msg)
        rows = self.candle.to_rows(rslt['payload'],key=key)
        # print('server',rslt['time'])
        # print('traded',rows[0].time)

        return rows

if __name__ == "__main__":
    import asyncio
    upbit = Upbit()
    print(upbit.get_candle())



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
    import pandas as pd
    async def main():
        async with upbit.xclient() as xclient:
            # rslt = await upbit.xget_candle_last(xclient,count=5,msg=True)
            rslt = await upbit.candle.xget(
                xclient=xclient,to=None,count=5,msg=True,)
            
        rows = upbit.candle.to_rows(rslt['payload'],key='namedtuple')
        last = upbit.candle.last_time(rslt['time'])
        rows = rows[1:]
        print(pd.DataFrame(rows))
        # print(ksts.close)
        # print(rows[1].time)

        print(last)

        # rows[0] : trade, 
        # rows[1] : last,
        if rows[1].time == 0:
        # if rows[1].time == last.close:
            print('case 1 : upload rows[1] : 정상')
        elif rows[0].time == last.close:
                if last.last.second >=3:
                    print('case 2 : upload rows[0] : 3초 이상 동안 새로운 거래가 없어')
                else:
                    print('case 3 : retry : 3초 미만 동안 새로운 거래가 없음 혹시 모르니 다시 시도')
        else:
            all_times = [row.time for row in rows]
            if last.close not in all_times:
                print('case 4 : upload zero candle : 1분 이상 새로운 거래가 없었음')
                prev_price = rows[0].close
                zero_candle = rows[0]._replace(
                    time=last.close, open=prev_price, high=prev_price, low=prev_price, 
                    close=prev_price, amount=0, volume=0)
            else:
                print('case 5 : unknown case Raise Error')
                print(pd.DataFrame(rows))
                print(last)


        
    #     print(upbit.candle.last_time(rslt['time']))
    # asyncio.run(main())
