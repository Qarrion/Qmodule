import logging
from turtle import up
from Qupbit.models import Market, Candle
from Qupbit.utils.logger_custom import CustomLog
import httpx

class Upbit:
    def __init__(self, logger:logging.Logger):
        self._custom  = CustomLog(logger,'async')
        self.market = Market(logger)
        self.candle = Candle(logger)

    def xclient(self):
        """>>> return httpx.AsyncClient() """
        return httpx.AsyncClient()

    def get_market(self, quote:str=None, base:str=None) -> list:
        payload = self.market.get('payload')
        filtered = self.market.parser.market(payload, 'market', qoute=quote, base=base)
        rows = self.market.to_rows(filtered)
        return rows

    async def xget_market(self, xclient:httpx.AsyncClient, quote:str=None, base:str=None) -> list:
        payload = await self.market.xget(xclient,'payload')
        filtered = self.market.parser.market(payload, 'market', qoute=quote, base=base)
        rows = self.market.to_rows(filtered)
        return rows


    def get_candle(self):
        pass

if __name__ == "__main__":
    from Qupbit.utils.logger_color import ColorLog
    lgger = ColorLog('upbit', 'green')
    upbit = Upbit(lgger)
    rslt = upbit.get_market('KRW')
    print(rslt)

    import asyncio

    async def main():
        async with upbit.xclient() as xclient:
            rslt = await upbit.xget_market(xclient,'KRW')
        print(rslt)

    asyncio.run(main())


