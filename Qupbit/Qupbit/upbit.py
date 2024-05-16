import logging
from turtle import up

import requests
from Qupbit.models import Market, Candle
from Qupbit.utils.logger_custom import CustomLog
import httpx

class Upbit:
    def __init__(self, name:str='consume'):
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom  = CustomLog(logger,'async')
        self._custom.info.msg('Upbit')
        self.market = Market(logger)
        self.candle = Candle(logger)

    def xclient(self):
        """>>> return httpx.AsyncClient() """
        return httpx.AsyncClient()

    def get_market(self, session:requests.Session=None, quote:str=None, base:str=None) -> list:
        """+ response -> result -> payload -> to_load"""
        payload = self.market.get(session,'payload')
        filtered = self.market.parser.market(payload, 'market', quote=quote, base=base)
        rows = self.market.to_rows(filtered)
        return rows

    async def xget_market(self, xclient:httpx.AsyncClient, quote:str=None, base:str=None) -> list:
        """+ response -> result -> payload -> to_load"""
        payload = await self.market.xget(xclient,'payload')
        filtered = self.market.parser.market(payload, 'market', quote=quote, base=base)
        rows = self.market.to_rows(filtered)
        return rows

    def get_candle(self,session:requests.Session=None,market:str='KRW-BTC',to:str=None,count:int=200):
        """+ response -> result -> payload -> to_load"""
        payload = self.candle.get(
            session=session,market=market,to=to,count=count,tz='KST',key='payload')
        rows = self.candle.to_rows(payload)
        return rows
    
    async def xget_candle(self, xclient:httpx.AsyncClient,market:str='KRW-BTC',to:str=None,count:int=200):
        """+ response -> result -> payload -> to_load"""
        payload = await self.candle.xget(
            xclient=xclient,market=market,to=to,count=count,tz='KST',key='payload')
        rows = self.candle.to_rows(payload)
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
            rslt = await upbit.xget_candle(xclient,count=10)
        print(rslt)

    asyncio.run(main())
