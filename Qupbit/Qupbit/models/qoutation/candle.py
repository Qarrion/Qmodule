# ---------------------------------------------------------------------------- #
#     https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1    #
# ---------------------------------------------------------------------------- #
import asyncio
from collections import namedtuple
from re import L
import httpx
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.tools.parser import Parser
from Qupbit.tools.timez import Timez
from datetime import datetime, timedelta
from dateutil import parser
from typing import Literal, List
import requests
import logging


class Candle:
    """ >>> #
    candle = Candle()
    candle.get('KRW-BTC', to, 5,'KST')
    """
    url_candle='https://api.upbit.com/v1/candles/minutes/1'
    headers = {"Accept": "application/json"}

    def __init__(self, name:str='candle'):
        try:
            from Qlogger import Logger
            logger = Logger(name, 'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger,'async')
        self.parser = Parser()
        self.timez = Timez()

    def get(self, session:requests.Session=None, 
            market:str='KRW-BTC', to:str=None, count:int=200, tz:Literal['UTC','KST']='KST',
            key:Literal['status','header','payload','remain','text']=None, msg=False):
        """ >>> # 
        totz = self._arg_to(date_time_str=to, tz=tz) if to is not None else None
        return result
        """

        totz = self._to_api_to(date_time_str=to, tz=tz) if to is not None else None
        # print(f"[totz] {totz}")
        params=dict(market = market, count = count, to = totz)

        if session is None:
            resp = requests.get(url=self.url_candle, headers=self.headers, params=params)
        else:
            resp = session.get(url=self.url_candle, headers=self.headers, params=params)

        rslt = self.parser.response(resp)
        if msg : self._msg_result(status='candle',result=rslt,market=market,frame="api") 
        if key is not None: rslt = rslt[key]
        return rslt		

    async def xget(self, xclient:httpx.AsyncClient=None, 
                   market:str='KRW-BTC', to:str=None, count:int=200, tz:Literal['UTC','KST']='KST',
                   key:Literal['status','header','payload','remain','text']=None, msg=False):
        is_context = False
        if xclient is None:
            xclient = httpx.AsyncClient()
            is_context = True

        totz = self._to_api_to(date_time_str=to, tz=tz) if to is not None else None
        params=dict(market = market, count = count, to = totz)
        resp = await xclient.get(url=self.url_candle, headers=self.headers, params=params)
        rslt = self.parser.response(resp)
        if msg : self._msg_result(status='candle',result=rslt,market=market,frame="xapi") 
        if key is not None: rslt = rslt[key]

        if is_context : await xclient.aclose()
        return rslt			

    def _to_api_to(self, date_time_str:str, tz:Literal['UTC','KST']='KST') -> str:
        date_time = parser.parse(date_time_str)
        if self.timez.is_aware(date_time):
            date_time_aware = self.timez.as_timezone(date_time, tz)
        else:
            date_time_aware = self.timez.as_localize(date_time, tz)

        if tz=='UTC':
            to = datetime.strftime(date_time_aware,'%Y-%m-%dT%H:%M:%SZ')
        elif tz == 'KST':
            to = date_time_aware.isoformat(sep='T',timespec='seconds')
        return to
    
    def last_time(self, naive:datetime=None, msg=False):
        """>>> return Last(time, stable, close, trade)"""
        if naive is None:
            naive=datetime.now()
        assert not self.timez.is_aware(naive) , "invalid aware datetime"

        if naive.second==0:
            naive_stable = naive.replace(second=1,microsecond=0)           
        else:
            naive_stable = naive

        last_trade = naive.replace(second=0,microsecond=0)
        last_close = last_trade + timedelta(minutes=-1)

        naive_str = self.timez.to_str(naive,2)
        stable_str = self.timez.to_str(naive_stable,2)
        close_str = self.timez.to_str(last_close,2)
        trade_str = self.timez.to_str(last_trade,2)

        if msg: print(f" + naive({naive_str}) close({close_str}), trade({trade_str})")
        Last = namedtuple('Last',['time','stable','close','trade'])
        return Last(naive_str, stable_str, close_str, trade_str)
        
    def _to_sql_kst(self, date_time_str:str):
        date_time_navie = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S') 
        return self.timez.as_localize(date_time_naive=date_time_navie,tz='KST')
    
    def to_rows(self, payload:List[dict],key:Literal['tuple','namedtuple']='tuple'):
        """
        + market, (candle_date_time_utc), candle_date_time_kst[str->localize], 
        + opening_price, high_price, low_price, trade_price,
        + (timestamp), candle_acc_trade_price, candle_acc_trade_volume, (unit)"""
        selected_rows =[
            (
                d['market'], 
                # self.timez.as_localize(d['candle_date_time_kst'],'KST'),
                self._to_sql_kst(d['candle_date_time_kst']),
                # d['candle_date_time_kst'],
                d['opening_price'],d['high_price'],d['low_price'],d['low_price'],
                d['candle_acc_trade_price'], d['candle_acc_trade_volume']
            ) 
                for d in payload
        ]
        if key=='namedtuple':
            Candle = namedtuple('Candle',['market','time','open','high','low','close','amount','volume'])
            selected_rows = [Candle(*item) for item in selected_rows]

        return selected_rows        

    def _msg_result(self,status, result:dict, market, frame:str):
        remain = result['remain']
        if result['status'] == 200:
            self._custom.debug.msg(status, remain['group']+"/g",f"{remain['sec']}/s", market, frame=frame)
        else:
            self._custom.error.msg(status, result['text'], frame=frame)   

if __name__=='__main__':
    import pandas as pd
    from Qupbit.tools.timez import Timez
    from Qupbit.utils.print_divider import eprint

    candle = Candle()
    # print(candle._to_api_to('2023-01-01T00:00:00+09:00','KST'))
    # print(candle._to_api_to('2023-01-01T00:00:00','UTC'))

    # str_kst ='2023-01-01T00:00:00'
    str_kst ='2024-01-01T06:05:00'
    print(str_kst)
    rows = candle.get(to=str_kst, tz='KST',count=5, key='payload',msg=True)
    print(pd.DataFrame(rows))
    # from datetime import datetime   
    # print(candle.last_time(datetime(2024,1,1,5,5,1,1)))
    # print(candle.last_time(datetime(2024,1,1,5,5,0,0)))

    # print(dt:=datetime(2024,1,1,5,5,0,1))
    # (last_time, last_close, last_trade) = candle.last_time(dt,msg=True)
    # print(last_time)
    # print(candle._to_api_to(last_time,'KST'))
    # rows = candle.get(to=last_time, tz='KST',count=5, key='payload',msg=True)
    # print(pd.DataFrame(rows))
    # ------------------------------------------------------------------------ #
    #                                 get last                                 #
    # ------------------------------------------------------------------------ #



    # resp = candle.get(None, 'KRW-POLYX', '2020-01-01 00:00:01', 10,'KST',msg=True)
    # eprint("response")
    # print(resp.keys())

    # eprint("payload")
    # print(resp['payload'])
    # payload = candle.get(None, 'KRW-ETH', None, 3,'KST','payload')
    # print(payload)

    # eprint("dataframe")
    # print(pd.DataFrame(resp['payload']))

    # eprint('rows') 
    # print(candle.to_rows(payload))


    # ------------------------------------------------------------------------ #
    #                                get continue                              #
    # ------------------------------------------------------------------------ #
    # to = candle.timez.from_str('2020-01-01 00:00:01')
    # to = candle.timez.as_timezone(to,'UTC')
    # to = candle.timez.to_str_upbit(to,'UTC')
    # print(to)
    # resp = candle.get(None, 'KRW-POLYX', to, 10,'UTC',msg=True)
    # resp = candle.get(None, 'KRW-POLYX', '2019-12-31T23:59:01Z', 10,'UTC',msg=True)
    # resp = candle.get(None, 'KRW-POLYX', '2020-01-01 00:10:01', 10,'KST',msg=True)
    # print(pd.DataFrame(resp['payload']))
    # eprint('get') 
    # to ='2021-10-10T00:00:00+09:00'
    # print(to)
    # candle._arg_to(to,tz='UTC')
    # candle._arg_to(to,tz='KST')

    # resp0 = candle.get(None, 'KRW-BTC', to, 5,'KST')
    # print(pd.DataFrame(resp0['payload']))

    # eprint('kst') 
    # to = resp0['payload'][-1]['candle_date_time_kst']
    # totz = candle._arg_to(to,'KST')
    # print(to)
    # print(totz)
    # resp1 = candle.get(None,'KRW-BTC', totz, 5,'KST')
    # print(pd.DataFrame(resp1['payload']))

    # eprint('utc') 
    # to = resp0['payload'][-1]['candle_date_time_utc']
    # totz = candle._arg_to(to,'UTC')
    # print(to)
    # print(totz)
    # resp1 = candle.get(None,'KRW-BTC', totz, 5,'KST')
    # print(pd.DataFrame(resp1['payload']))
    
    # ------------------------------ timestamp? ------------------------------ #
    # tmp = pd.DataFrame(resp0['payload'])
    # tmp = tmp[['candle_date_time_utc','candle_date_time_kst','timestamp']]
    # tmp['sdt'] = tmp['timestamp'].apply(candle.timez.from_stamp)
    # tmp


    # --------------------------------- util --------------------------------- #
    # from datetime import datetime
    # naive = datetime.now()
    # print(naive)

    # close, trade = candle.to_ftime(naive,msg=True)


    # --------------------------------- other -------------------------------- #
    # # timez = Timez()
    # # timez.from_stamp(1633794600053/1000)
    # # print(timez.now())
    # # print(datetime.strftime(timez.now(),'%Y-%m-%dT%H:%M:%SZ'))
    # # print(datetime.strftime(timez.now('KST'),'%Y-%m-%dT%H:%M:%SZ'))
    # # print(datetime.strftime(timez.now('UTC'),'%Y-%m-%dT%H:%M:%SZ'))

    # # KRW-BTC  2024-05-02T12:17:00  2024-05-02T21:17:00  1714652221622
    # stamp_like = 1714652221622
    # Timez.from_stamp(Timez._to_ten_digit(stamp_like),'KST')

    # --------------------------------- async -------------------------------- #
    async def main():
        await candle.xget(msg=True)

    asyncio.run(main())