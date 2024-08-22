# ---------------------------------------------------------------------------- #
#     https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1    #
# ---------------------------------------------------------------------------- #
from Qlogger import Logger
from Qupbit.tools import timez
from Qupbit.tools.parser import Parser
from Qupbit.tools.timez import Timez
from collections import namedtuple
from datetime import datetime, timedelta
from dateutil import parser
from typing import Literal, List
from datetime import datetime
import asyncio
import httpx
import requests

Row = namedtuple('Row',['time','market','open','high','low','close','amount','volume'])
Last = namedtuple('Last',['input','stable','close','trade'])

class Candle:    

    # time period change? -> _zero_volume_row
    url_candle='https://api.upbit.com/v1/candles/minutes/1'
    headers = {"Accept": "application/json"}
    max_count = 200

    def __init__(self,name:str='candle',msg=False):
        self._logger = Logger(name,clsname='Candle',msg=False)
        self._parser = Parser()
        self._row = Row
        self._timez = Timez()
        self.dtime = datetime

    def dtime_kst(self, year, month, day, hour, minute):
        return self._timez.tz_dict['KST'].localize(datetime(year=year,month=month,day=day,hour=hour,minute=minute))

    def get(self, market:str, to:datetime, count:int=200, payload = True, msg=False):
        """ 
        + market:'KRW-BTC'
        + to: dtime aware (not None)
        + tz: timezone (localized)
        """

        # ----------------------------- requests ----------------------------- #
        # last = self.to_last(to)
        arg_to = self._dtime_to_arg(dtime=to)
        params=dict(market = market, count = count, to = arg_to)
        resp = requests.get(url=self.url_candle, headers=self.headers, params=params)
        rslt = self._parser.response(resp)

        # ----------------------------- exception ---------------------------- #
        stime = self._timez._stime_aware_to_naive(arg_to, 1)
        # if rslt['time'] < last.trade:
        #     stime_sv = self._timez._stime_aware_to_naive(self._dtime_to_arg(rslt['time']), 1)
        #     self._logger.error.msg(f'{market=:}',stime, stime_sv,'too early!')    
        #     raise Exception('too early')
        
        if rslt['status'] == 200:
            if msg : self._logger.info.msg(f'{market=:}', stime, rslt['remain'])

        elif rslt['status'] == 429:
            self._logger.error.msg(f'{market=:}',stime, f"code({rslt['status']})", 'too_many_requests!')    

        else:
            self._logger.error.msg(f'{market=:}',stime, f"code({rslt['status']})", rslt['text'])    
            print(rslt['text'])

        # ------------------------------ return ------------------------------ #
        resp.raise_for_status()
        if payload: rslt = rslt['payload']
        return rslt

    async def xget(self, xclient:httpx.AsyncClient, market:str, to:datetime, 
                   count:int=200, payload = True, msg=False):
        """
        + market:'KRW-BTC'
        + to: dtime aware (not None)
        + tz: timezone (localized)
        """
        # ----------------------------- requests ----------------------------- #
        # to_stable = to.replace(second=1,microsecond=0)
        # to_trade = to_stable.replace(second=0)
        arg_to = self._dtime_to_arg(dtime=to)
        params=dict(market = market, count = count, to = arg_to)
        resp = await xclient.get(url=self.url_candle, headers=self.headers, params=params)
        rslt = self._parser.response(resp)

        # ----------------------------- exception ---------------------------- #
        # if rslt['time'] < to_trade:
        #     stime_sv = self._timez._stime_aware_to_naive(self._dtime_to_arg(rslt['time']), 1)
        #     self._logger.error.msg(f'{market=:}',stime, stime_sv,'too early!')    
        #     raise Exception('too early')
        
        stime = self._timez._stime_aware_to_naive(arg_to, 1)
        if rslt['status'] == 200:
            if msg : self._logger.info.msg(f'{market=:}', stime, rslt['remain'])

        elif rslt['status'] == 429:
            self._logger.error.msg(f'{market=:}', stime, f"code({rslt['status']})", 'too_many_requests!')    

        else:
            self._logger.error.msg(f'{market=:}', stime, f"code({rslt['status']})", rslt['text'])    

        # ------------------------------ return ------------------------------ #
        resp.raise_for_status()
        if payload: rslt = rslt['payload']
        return rslt	

    def to_last(self, dtime:datetime, msg=False):
        """>>> # Last namedtuple / self._timez.to_str(input, fmt=2 )
        return Last(input, stable, close, trade)"""
 
        input = dtime
        stable = dtime if dtime.second!=0 else dtime.replace(second=1,microsecond=0)
        trade = dtime.replace(second=0,microsecond=0)
        close = trade + timedelta(minutes=-1)

        if msg: print(f" + input({input}) stable({stable}) close({close}), trade({trade})")
        return Last(input, stable, close, trade)

    def to_rows(self, payload:List[dict], fmt=1):
        """
        >>> namedtuple('Candle',['time','market','open','high','low','close','amount','volume'])
        + fmt = 0 : datetime naive
        + fmt = 1 : datetime aware kst
        """
        selected_rows =[
            Row(self._stime_to_fmt(d['candle_date_time_kst'],fmt=fmt),
                d['market'], 
                d['opening_price'],d['high_price'],d['low_price'],d['trade_price'],
                d['candle_acc_trade_price'], d['candle_acc_trade_volume']) 
                for d in payload ]
        return selected_rows        
    
    def to_dict(self, row:Row):
        if isinstance(row, Row):
            return row._asdict()
        else:
            print(f"\033[31m row is not instance Row({Row.index} \033[0m")

    def to_complete_zero_volume(self, rows:List[Row], dtime_trade:datetime, cut_trade:bool):
        """ 
        + dtime_trade : aware
        + cut_trade : trade (incomplete) close (complete)
        """
        # dtime_now_trade_naive = self._timez.as_naive(dtime_trade)
        # dtime_now_trade_kst = self._timez.as_localize(dtime_now_trade_naive, tz='KST')

        # 기본적으로 to 조회시 완성되지 않은 trade시간이 rows[0]에 포함
        # 즉 rows[0].time == dtime_now_trade_kst 임 -> 최종 cut
        if rows[0].time < dtime_trade:
            row_zero = self._zero_volume_row(prev_row=rows[0], new_dtime=dtime_trade)
            rows.insert(0,row_zero)
        
        rows_add = []
        for i, row_big in enumerate(rows[:-1]):
            row_small = rows[i+1]

            while row_big.time != row_small.time + timedelta(minutes=1):
                row_zero = self._zero_volume_row(
                    prev_row = row_small,
                    new_dtime = row_small.time + timedelta(minutes=1)
                    )
                rows_add.append(row_zero)
                row_small = row_zero

        rows.extend(rows_add)
        rows.sort(key=lambda x:x.time, reverse=True)

        if cut_trade: del rows[0]

        return rows

    def _zero_volume_row(self, prev_row:Row, new_dtime:datetime):
        """zero volume, same close prev, time"""
        m = prev_row.market
        c = prev_row.close
        t = new_dtime
        return Row(market=m,time=t,open=c,high=c,low=c,close=c,amount=0,volume=0)

    # ------------------------------------------------------------------------ #
    #                                   utils                                  #
    # ------------------------------------------------------------------------ #

    def _dtime_to_arg(self, dtime:datetime, tz:Literal['KST','UTC']='KST') -> str:
        """dtime aware -> tz (as localize) -> upbit arg"""
        # dtime_naive = self._timez.as_naive(dtime)
        # dtime_aware = self._timez.as_localize(dtime_naive, tz)

        if tz=='KST':
            # dtime_naive = self._timez.as_naive(dtime)
            to = dtime.isoformat(sep='T',timespec='seconds')
            # print(to)
        elif tz == 'UTC':
            to = datetime.strftime(dtime,'%Y-%m-%dT%H:%M:%SZ')
        else:
            raise Exception('dtime must be timezone kst or utc')

        return to

    def _stime_to_fmt(self, stime:str, fmt=0):
        """
        %Y-%m-%dT%H:%M:%S
        + fmt = 0 : datetime naive
        + fmt = 1 : datetime aware kst
        """
        dtime_naive = self._timez.from_str(stime, fmt=0, only_naive=True)
        if fmt == 0:
            rslt = dtime_naive
        elif fmt == 1:
            rslt = self._timez.as_localize(date_time_naive=dtime_naive,tz='KST')
        return rslt


if __name__=='__main__':
    candle = Candle()
    import pandas as pd

    # ------------------------------- too many ------------------------------- #
    to = candle.dtime_kst(2020,10,10,0,0)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)
    # resp = candle.get(market='KRW-BTC',to=to,count=10, msg=True)

    # ---------------------------- only dtime_kst ---------------------------- #
    to = candle.dtime_kst(2020,10,10,0,0)
    print(to)
    resp = candle.get(market='KRW-BTT',to=to,count=10, msg=True)
    rows = candle.to_rows(resp)
    print(pd.DataFrame(rows))
    
    # # ------------------ last_to and to_complete_zero_volume ----------------- #
    # to = candle.dtime_kst(2020,10,9,23,55)
    # last = candle.to_last(to)
    # print(to)
    # resp = candle.get(market='KRW-BTT',to=last.stable,count=10, msg=True)
    # rows = candle.to_rows(resp)
    # print(pd.DataFrame(rows))

    # rows = candle.to_complete_zero_volume(rows,last.trade,True)
    # print(pd.DataFrame(rows))

    # rows = candle.to_complete_zero_volume(rows,last.trade,False)
    # print(pd.DataFrame(rows))

    # # ------------------------------- continue ------------------------------- #
    # last2 = candle.to_last(rows[-1].time)
    # resp2 = candle.get(market='KRW-BTT',to=last2.stable,count=10, msg=True)
    # rows2 = candle.to_rows(resp2)
    # rows2 = candle.to_complete_zero_volume(rows2,last2.trade,True)
    # print(pd.DataFrame(rows2))

    # # ------------------------------------------------------------------------ #
    # # ------------------------------------------------------------------------ #
    # # ------------------------------------------------------------------------ #




    # # -------------------------------- asyncio ------------------------------- #
    # async def main():
    #     async with httpx.AsyncClient() as xclient:
    #         to = candle.dtime_kst(2020,10,10,0,0)
    #         resp = await candle.xget(xclient=xclient,market='KRW-BTC',to=to, count=1, msg=True)
    #         resp = await candle.xget(xclient=xclient,market='KRW-BTC',to=to, count=5,msg=True)
    #         resp = await candle.xget(xclient=xclient,market='KRW-BTC',to=to, count=5,msg=True)
    #         resp = await candle.xget(xclient=xclient,market='KRW-BTC',to=to, count=5,msg=True)

    #         rows = candle.to_rows(resp)
    #         print(pd.DataFrame(data=rows))

    # asyncio.run(main())
