from datetime import datetime
from typing import Literal
import requests
import ntplib
import pytz
import time




class nowts:

    tz_dict = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')
    }

    @classmethod
    def _fetch_ntp_time(cls):
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", version=3)
        return response.tx_time

    @classmethod
    def _fetch_worldtimeapi(cls):
        response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC')
        data = response.json()
        unix_timestamp = data['unixtime']
        return float(unix_timestamp)

    @classmethod
    def _fetch_time_now(cls):
        return time.time()
    
    @classmethod
    def _get_accurate_time(cls)-> float:
        """return timestamp (now)
        1. ntp:pool.ntp.org
        2. http://worldtimeapi.org/api/timezone/Etc/UTC
        3. time.time()"""
        for func in [cls._fetch_ntp_time, cls._fetch_worldtimeapi, cls._fetch_time_now]:
            try:
                now = func()
                return now 
            except Exception as e:
                pass
    
    @classmethod
    def get_float(cls):
        """return timestamp(10 digit)"""
        return cls._get_accurate_time()

    @classmethod
    def get_datetime(cls,tz:Literal['KST','UTC'], to_naive=True):
        timezone = cls.tz_dict[tz]
        nowts = cls.get_float()
        now = datetime.fromtimestamp(nowts,tz=timezone)     # aware
        if to_naive : now = now.replace(tzinfo=None)        # naive
        return now

    @classmethod
    def check(cls):
        print('  ntp',cls._fetch_ntp_time())
        print('world',cls._fetch_worldtimeapi())
        print(' time',cls._fetch_time_now())


if __name__ == "__main__":
    print("# --------------------------------- check -------------------------------- #")
    nowts.check()
    print("# ------------------------------- get_float ------------------------------ #")
    print(nowts._get_accurate_time())
    print("# -------------------------- get_datetime naive -------------------------- #")
    print('KST', nowts.get_datetime('KST'),nowts.get_datetime('KST').tzinfo)
    print('UTC', nowts.get_datetime('UTC'),nowts.get_datetime('UTC').tzinfo)
    print("# -------------------------- get_datetime aware -------------------------- #")
    print('KST', nowts.get_datetime('KST',False),nowts.get_datetime('KST',False).tzinfo)
    print('UTC', nowts.get_datetime('UTC',False),nowts.get_datetime('UTC',False).tzinfo)