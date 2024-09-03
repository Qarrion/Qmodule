from typing import Literal
from Qupbit.modules.market import Market
from Qupbit.modules.candle import Candle
from Qupbit.tools.timez import Timez
from Qlogger import Logger
from datetime import datetime
import httpx



    


class Upbit:

    def __init__(self, name='upbit'):
        self.candle = Candle()
        self.market = Market()
        self.timez = Timez()
        self._logger = Logger(logname=name, clsname='Upbit',msg=False)
        self._logger.set_sublogger(sublogger=self.candle._logger)
        self._logger.set_sublogger(sublogger=self.market._logger)

    # --------------------------------- utils -------------------------------- #
    def dtime_kst(self, year, month, day, hour, minute):
        return self.candle.dtime_kst(year, month, day, hour, minute)

    def dtime_kst_now(self):
        return self.timez.now(tz='KST')

    # -------------------------------- market -------------------------------- #
    async def xget_market(self, session:httpx.AsyncClient, 
                          quote: Literal['KRW', 'BTC', 'USDT'] = None, base= None, msg=False):
        rslt = await self.market.xget(xclient=session,quote=quote,base=base,payload=True,msg=msg)
        rows = self.market.to_rows(rslt)

        return rows

    # -------------------------------- candle -------------------------------- #

    async def xget_m1_stable(self, xclient:httpx.AsyncClient, market:str, to:datetime, 
                   count:int=200, msg=False, remain=False):
        """if remain return(rows, rslt) else return rows"""
        last = self.candle.to_last(dtime=to)
        rslt = await self.candle.xget(xclient=xclient, market=market, to=last.stable, 
                        count=count, payload=False, msg=msg)
        if rslt['time'] < last.trade:
            stime_sv = self.candle._timez.to_str(rslt['time'], 1)
            stime_cl = self.candle._timez.to_str(to, 1)
            self._logger.error.msg(f'{market=:}',stime_cl, stime_sv,'too early!')    
            raise Exception('too early')
    
        rows = self.candle.to_rows(rslt['payload'])
        rows = self.candle.to_complete_zero_volume(rows=rows,
                                                dtime_trade=last.trade,cut_trade=True)
        if remain:
            return rows, rslt['remain']
        else:
            return rows
    
    def get_m1_stable(self, market:str, to:datetime, 
                   count:int=200, msg=False, remain=False):
        
        last = self.candle.to_last(dtime=to)
        rslt = self.candle.get(market=market, to=last.stable, 
                        count=count, payload=False, msg=msg)
        
        if rslt['time'] < last.trade:
            stime_sv = self.candle._timez.to_str(rslt['time'], 1)
            stime_cl = self.candle._timez.to_str(to, 1)
            self._logger.error.msg(f'{market=:}',stime_cl, stime_sv,'too early!')    
            raise Exception('too early')
    
        rows = self.candle.to_rows(rslt['payload'])
        rows = self.candle.to_complete_zero_volume(rows=rows,
                                                dtime_trade=last.trade,cut_trade=True)
        if remain:
            return rows, rslt['remain']
        else:
            return rows


if __name__ == "__main__":
    import pandas as pd
    import asyncio
    upbit = Upbit()

    # print(upbit.timez.now(tz='KST'))

    to = upbit.dtime_kst(2020,10,10,0,0)
    rows = upbit.get_m1_stable(market='KRW-BTT', to=to, msg=True)
    pd.DataFrame(data=rows)


    # ------------------------------------------------------------------------ #
    # async def main():
    #     to = upbit.dtime_kst(2020,10,10,1,1)
    #     async with httpx.AsyncClient() as xclient:
    #         await upbit.xget_m1_stable(xclient=xclient,market='KRW-BTC', to=to)

    # asyncio.run(main())