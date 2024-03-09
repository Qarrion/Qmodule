# ---------------------------------------------------------------------------- #
#     https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1    #
# ---------------------------------------------------------------------------- #
import requests
from Qupbit.tools.parser import Parser
from Qupbit.tools.tracer import Tracer 
from Qupbit.tools.timez import Timez
import logging
from dateutil import parser
from typing import Literal


class Candle:

    url_candle='https://api.upbit.com/v1/candles/minutes/1'
    headers = {"Accept": "application/json"}

    def __init__(self, logger:logging.Logger=None, debug=True):
        self.tracer = Tracer(logger)
        self.parser = Parser()
        self.timez = Timez()
        self._debug = debug

    def requests_get(self,market:str, to:str, count:int=200):
        params=dict(market = market, count = count, to = to)
        resp = requests.get(url=self.url_candle, headers=self.headers, params=params)
        return resp
    
    def get(self, market:str, to:str, count:int=200, tz:Literal['UTC','KST']='KST'):
        """status, header, payload, remain[group, min, sec], text"""
        totz = self.arg_to(date_time_str=to, tz=tz)
        resp = self.requests_get(market=market, to=totz, count=count)
        rslt = self.parser.response(resp)
        if self._debug : self.tracer.debug.request('candle',rslt) 
        return rslt		
    
    def get_hist(self, market:str, to:str, fr:str, count:int=200, tz:Literal['UTC','KST']='KST'):
        totz = self.arg_to(to, tz)
        fmtz = self.arg_to(fr, tz)


    def arg_to(self, date_time_str:str, tz:Literal['UTC','KST']='KST'):
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

if __name__=='__main__':
    import pandas as pd
    from Qupbit.tools.timez import Timez
    from Qlogger import Logger
    logger = Logger('test','head')
    candle = Candle(logger)

    print('# ---------------------------------- get --------------------------------- #')
    to ='2021-10-10T00:00:00+09:00'
    # candle.arg_to(arg, 'KST')
    # to = candle.arg_to(arg, 'KST')
    resp = candle.get('KRW-BTC',to,10)
    pd.DataFrame(resp['payload'])

    date_time_str_naive_kst = resp['payload'][-1]['candle_date_time_kst']
    to = candle.arg_to(date_time_str_naive_kst, 'KST')
    resp = candle.get('KRW-BTC',to,10)
    pd.DataFrame(resp['payload'])




    print('# ---------------------------------- get --------------------------------- #')
    arg ='2021-10-10T00:00:00+09:00'
    candle.arg_to(arg, 'UTC')
    to = candle.arg_to(arg, 'UTC')
    resp = candle.get('KRW-BTC',to,10)
    pd.DataFrame(resp['payload'])

    date_time_str_naive_utc = resp['payload'][-1]['candle_date_time_utc']
    to = candle.arg_to(date_time_str_naive_utc, 'UTC')
    resp = candle.get('KRW-BTC',to,10)
    pd.DataFrame(resp['payload'])


# ---------------------------------------------------------------------------- #

    from datetime import datetime
    timez = Timez()
    timez.now()
    datetime.strftime(timez.now(),'%Y-%m-%dT%H:%M:%SZ')
    datetime.strftime(timez.now('KST'),'%Y-%m-%dT%H:%M:%SZ')
    datetime.strftime(timez.now('UTC'),'%Y-%m-%dT%H:%M:%SZ')


    
    arg ='2021-10-10T00:00:11+09:00'

    to = candle.arg_to(arg, 'KST')


    dtm_kst = timez.from_str(arg)
    timez.to_str(dtm_kst,7)

    now_kst = timez.now('KST')
    now_utc = timez.now('UTC')
    timez.to_str(now_kst,7)
    timez.to_str(now_utc,7)


    arg = timez.now('KST').isoformat()
    arg = timez.now('KST').isoformat(sep='T',timespec='seconds')
    print(arg)
    arg = timez.now().isoformat(sep='T',timespec='seconds')
    print(arg)

    rslt = candle.get('KRW-BTC', 20, arg)
    str1 = rslt['payload'][0]['candle_date_time_kst']
    str2 = rslt['payload'][-1]['candle_date_time_kst']
    print('from', str2, 'to', str1, 'arg_to',arg)   

    timez.now('KST')
    timez.now('KST').isoformat()
    timez.to_str(timez.now('KST'),7)


    # now_str = timez.to_str(timez.now('KST'),4)

    # to = candle.arg_to('2021-10-10T00:00:11+09:00')
    # print('to',to)
    # rslt = candle.get('KRW-BTC', 20, '2021-10-10T00:00:11+09:00')
    # rslt['url']
    # str1 = rslt['payload'][0]['candle_date_time_kst']
    # str2 = rslt['payload'][-1]['candle_date_time_kst']
    # print('from', str2, 'to', str1, 'arg_to',to)


    # # pd.DataFrame(data=rslt['payload'])

    # # ------------------------------------------------------------------------ #
    arg = str2
    rslt = candle.get('KRW-BTC', 20, arg)
    str1 = rslt['payload'][0]['candle_date_time_kst']
    str2 = rslt['payload'][-1]['candle_date_time_kst']
    print('from', str2, 'to', str1, 'arg_to',arg)
    # pd.DataFrame(data=rslt['payload'])


    # print('# --------------------------------- test --------------------------------- #')
    # candle.test(rslt,header=True, column=True)

    # print('# -------------------------------- filter -------------------------------- #')
    # rslt_filtered = candle.filter(rslt['payload'], market='KRW-BTC')
    # print("KRW-BTC", len(rslt_filtered))
    # print(rslt_filtered)

    # rslt_filtered = candle.filter(rslt['payload'], qoute='KRW')
    # print("qoute-KRW", len(rslt_filtered))

    # rslt_filtered = candle.filter(rslt['payload'], base='BTC')
    # print("base-BTC", len(rslt_filtered))