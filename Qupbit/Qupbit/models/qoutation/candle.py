# ---------------------------------------------------------------------------- #
#     https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1    #
# ---------------------------------------------------------------------------- #
from Qupbit.utils.log_custom import CustomLog
from Qupbit.tools.parser import Parser
from Qupbit.tools.timez import Timez
from datetime import datetime
from dateutil import parser
from typing import Literal
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
        self.custom = CustomLog(logger,'async')
        self.parser = Parser()
        self.timez = Timez()
        self._debug = debug

    def _req_get(self, market:str, to:str, count:int=200):
        """return response"""
        params=dict(market = market, count = count, to = to)
        resp = requests.get(url=self.url_candle, headers=self.headers, params=params)
        return resp
    
    def get(self, market:str, to:str, count:int=200, tz:Literal['UTC','KST']='KST'):
        """ >>> return result
        # status, header, payload, remain[group, min, sec], text"""
        totz = self._arg_to(date_time_str=to, tz=tz)
        resp = self._req_get(market=market, to=totz, count=count)
        rslt = self.parser.response(resp)
        if self._debug : self._msg_result('candles',rslt) 
        return rslt		

    def _arg_to(self, date_time_str:str, tz:Literal['UTC','KST']='KST'):
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
    
    def _msg_result(self,group, result:dict):
        remain = result['remain']
        status = result['status']
        if status == 200:
            self.custom.debug.msg(group, remain['group']+"/g", f"{remain['min']}/m",f"{remain['sec']}/s",back=2)
        else:
            self.custom.error.msg(group, result['text'],back=2)   

if __name__=='__main__':
    import pandas as pd
    from Qupbit.tools.timez import Timez
    from Qupbit.utils.print_divider import eprint
    from Qlogger import Logger

    logger = Logger('test','head')
    candle = Candle(logger)

    # ------------------------------------------------------------------------ #
    eprint('get') 
    to ='2021-10-10T00:00:00+09:00'
    print(to)
    resp0 = candle.get('KRW-BTC', to, 5,'KST')
    print(pd.DataFrame(resp0['payload']))

    eprint('kst') 
    to = resp0['payload'][-1]['candle_date_time_kst']
    print(to)
    print(candle._arg_to(to,'KST'))
    resp = candle.get('KRW-BTC', to, 5,'KST')
    print(pd.DataFrame(resp['payload']))

    eprint('utc') 
    to = resp0['payload'][-1]['candle_date_time_utc']
    print(to)
    print(candle._arg_to(to,'UTC'))
    resp = candle.get('KRW-BTC', to, 5,'UTC')
    print(pd.DataFrame(resp['payload']))

    # ------------------------------------------------------------------------ #
    # from datetime import datetime
    # timez = Timez()
    # timez.from_stamp(1633794600053/1000)
    # print(timez.now())
    # print(datetime.strftime(timez.now(),'%Y-%m-%dT%H:%M:%SZ'))
    # print(datetime.strftime(timez.now('KST'),'%Y-%m-%dT%H:%M:%SZ'))
    # print(datetime.strftime(timez.now('UTC'),'%Y-%m-%dT%H:%M:%SZ'))

