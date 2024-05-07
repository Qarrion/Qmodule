# ---------------------------------------------------------------------------- #
#     https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1    #
# ---------------------------------------------------------------------------- #
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

    def __init__(self, logger:logging.Logger=None, debug=True):
        self._custom = CustomLog(logger,'async')
        self.parser = Parser()
        self.timez = Timez()
        self._debug = debug

    def get(self, session:requests.Session=None, 
            market:str='KRW-BTC', to:str=None, count:int=200, tz:Literal['UTC','KST']='KST',
            key:Literal['status','header','payload','remain','text']=None):
        """ >>> # 
        totz = self._arg_to(date_time_str=to, tz=tz) if to is not None else None
        return result
        """

        totz = self._arg_to(date_time_str=to, tz=tz) if to is not None else None
        params=dict(market = market, count = count, to = totz)

        if session is None:
            resp = requests.get(url=self.url_candle, headers=self.headers, params=params)
        else:
            resp = session.get(url=self.url_candle, headers=self.headers, params=params)

        rslt = self.parser.response(resp)
        if self._debug : self._msg_result('candles',rslt) 
        if key is not None: rslt = rslt[key]
        return rslt		

    async def xget(self, xclient:httpx.AsyncClient, 
                   market:str='KRW-BTC', to:str=None, count:int=200, tz:Literal['UTC','KST']='KST',
                   key:Literal['status','header','payload','remain','text']=None):
        totz = self._arg_to(date_time_str=to, tz=tz) if to is not None else None
        params=dict(market = market, count = count, to = totz)
        resp = await xclient.get(url=self.url_candle, headers=self.headers, params=params)
        rslt = self.parser.response(resp)
        if self._debug : self._msg_result('candles',rslt) 
        if key is not None: rslt = rslt[key]
        return rslt		

    def _arg_to(self, date_time_str:str, tz:Literal['UTC','KST']='KST') -> str:
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
    
    def to_ftime(self, naive:datetime, debug=False):
        """>>> return (last_close, last_close)"""
        assert not self.timez.is_aware(naive) , "invalid aware datetime"


        last_trade = naive.replace(second=0,microsecond=0)
        last_close = last_trade + timedelta(minutes=-1)

        naive_str = self.timez.to_str(naive,2)
        close_str = self.timez.to_str(last_close,2)
        trade_str = self.timez.to_str(last_trade,2)

        if debug: print(f" + naive({naive_str}) close({close_str}), trade({trade_str})")

        return (close_str, trade_str)
        
    def to_rows(self, payload:List[dict]):

        selected_rows =[
            (
                d['market'], d['candle_date_time_kst'],
                d['opening_price'],d['high_price'],d['low_price'],d['low_price'],
                d['candle_acc_trade_price'], d['candle_acc_trade_volume']
            ) 
                for d in payload
        ]
        return selected_rows        

    def _msg_result(self,group, result:dict):
        remain = result['remain']
        status = result['status']
        if status == 200:
            self._custom.debug.msg(group, remain['group']+"/g", f"{remain['min']}/m",f"{remain['sec']}/s",frame=2)
        else:
            self._custom.error.msg(group, result['text'],frame=2)   

if __name__=='__main__':
    import pandas as pd
    from Qupbit.tools.timez import Timez
    from Qupbit.utils.print_divider import eprint
    from Qupbit.utils.logger_color import ColorLog
    logger = ColorLog('test', 'green')
    candle = Candle(logger)

    # ------------------------------ session get ----------------------------- #
    resp = candle.get(None, 'KRW-ETH', None, 5,'KST')
    print(resp)
    print(pd.DataFrame(resp['payload']))
    resp = candle.get(None, 'KRW-ETH', None, 5,'KST','payload')
    # print(resp[0:5])

    # eprint('rows') 
    # print(candle.to_rows(resp))
    # ------------------------------------------------------------------------ #
    # eprint('get') 
    to ='2021-10-10T00:00:00+09:00'
    # print(to)
    # candle._arg_to(to,tz='UTC')
    # candle._arg_to(to,tz='KST')

    resp = candle.get(None, 'KRW-ETH', None, 5,'KST')
    print(pd.DataFrame(resp['payload']))

    # resp0 = candle.get('KRW-BTC', to, 5,'KST')
    # print(pd.DataFrame(resp0['payload']))

    # eprint('kst') 
    # to = resp0['payload'][-1]['candle_date_time_kst']
    # print(to)
    # print(candle._arg_to(to,'KST'))
    # resp = candle.get('KRW-BTC', to, 5,'KST')
    # print(pd.DataFrame(resp['payload']))

    # eprint('utc') 
    # to = resp0['payload'][-1]['candle_date_time_utc']
    # print(to)
    # print(candle._arg_to(to,'UTC'))
    # resp = candle.get('KRW-BTC', to, 5,'UTC')
    # print(pd.DataFrame(resp['payload']))

    # # ------------------------------------------------------------------------ #
    # tmp = pd.DataFrame(resp['payload'])
    # tmp = tmp[['candle_date_time_utc','candle_date_time_kst','timestamp']]
    # tmp['sdt'] = tmp['timestamp'].apply(candle.timez.from_stamp)
    # tmp

    # # ------------------------------------------------------------------------ #
    # # from datetime import datetime
    # # timez = Timez()
    # # timez.from_stamp(1633794600053/1000)
    # # print(timez.now())
    # # print(datetime.strftime(timez.now(),'%Y-%m-%dT%H:%M:%SZ'))
    # # print(datetime.strftime(timez.now('KST'),'%Y-%m-%dT%H:%M:%SZ'))
    # # print(datetime.strftime(timez.now('UTC'),'%Y-%m-%dT%H:%M:%SZ'))

    # # KRW-BTC  2024-05-02T12:17:00  2024-05-02T21:17:00  1714652221622
    # stamp_like = 1714652221622
    # Timez.from_stamp(Timez._to_ten_digit(stamp_like),'KST')