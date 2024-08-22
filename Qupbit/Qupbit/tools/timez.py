from dateutil import parser
from datetime import datetime
import pytz
from typing import Literal

class Timez():
    # UTC = pytz.timezone('UTC')
    # KST = pytz.timezone('Asia/Seoul')

    # upbit:4
    fmt_dict = {        
        1:'%Y-%m-%d %H:%M:%S',
        2:'%Y-%m-%dT%H:%M:%S',
        3:'%Y-%m-%d %H:%M:%S%z',
        4:'%Y-%m-%dT%H:%M:%S%z',
        5:'%Y-%m-%d %H:%M:%S.%f%z',
        6:'%Y-%m-%dT%H:%M:%S.%f%z',
        7:'%Y-%m-%dT%H:%M:%SZ',
        8:'%y.%m.%d %H:%M',
        9:'%H:%M'}
    

    # <DstTzInfo 'Asia/Seoul' LMT+8:28:00 STD> 
    now_kst = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    tz_dict = {
        "KST":now_kst.tzinfo,           #<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>
        "UTC":pytz.timezone('UTC')
    }
    # ------------------------------------------------------------------------ #
    #                              return datetime                             #
    # ------------------------------------------------------------------------ #
    @classmethod
    def now(cls,tz:Literal['KST','UTC']=None):
        """if tz is None : naive else aware"""
        if tz is None:
            ret = datetime.now()
        else:
            ret = datetime.now(cls.tz_dict[tz])
        return ret

    @staticmethod
    def as_naive(date_time_aware:datetime):
        return date_time_aware.replace(tzinfo=None)

    @classmethod
    def as_localize(cls, date_time_naive:datetime, tz:Literal['KST','UTC']="KST"):
        """date_time_naive -> date_time_loc(tz)
        """
        return cls.tz_dict[tz].localize(date_time_naive)

    @classmethod
    def as_timezone(cls, date_time_aware:datetime, tz:Literal['KST','UTC']="KST"):
        """date_time_aware -> date_time_ast(tz)
        """
        return date_time_aware.astimezone(cls.tz_dict[tz])
    
    # ------------------------------------------------------------------------ #
    #                                  to type                                 #
    # ------------------------------------------------------------------------ #
    @classmethod
    def to_str(cls, date_time:datetime, fmt:int=1):
        """>>> # date_time -> data_time_str(fmt)
        1:'%Y-%m-%d %H:%M:%S'
        2:'%Y-%m-%dT%H:%M:%S'
        3:'%Y-%m-%d %H:%M:%S%z'
        4:'%Y-%m-%dT%H:%M:%S%z'
        5:'%Y-%m-%d %H:%M:%S.%f%z'
        6:'%Y-%m-%dT%H:%M:%S.%f%z'
        7:'%Y-%m-%dT%H:%M:%SZ'
        8:'%y.%m.%d %H:%M'
        9:'%H:%M'
        """
        date_time_str = datetime.strftime(date_time, cls.fmt_dict[fmt])
        return date_time_str

    @staticmethod
    def is_aware(date_time:datetime):
        return date_time.tzinfo is not None
    
    def is_naive(date_time:datetime):
        return date_time.tzinfo is None

    @staticmethod
    def to_str_slice(date_time:datetime, date="%Y-%m-%d", time='%H:%M:%S'):
        date_str = datetime.strftime(date_time,date)
        time_str = datetime.strftime(date_time,time)
        return date_str, time_str

    @staticmethod
    def to_stamp(date_time:datetime):
        return date_time.timestamp()

    # ------------------------------------------------------------------------ #
    #                                 from type                                #
    # ------------------------------------------------------------------------ #
    @classmethod
    def from_str(cls, date_time_str, fmt:int=0, only_naive=False):
        """
        >>> #
        0: parser.parse
        1:'%Y-%m-%d %H:%M:%S'
        2:'%Y-%m-%dT%H:%M:%S'
        3:'%Y-%m-%d %H:%M:%S%z'
        4:'%Y-%m-%dT%H:%M:%S%z'
        5:'%Y-%m-%d %H:%M:%S.%f%z'
        6:'%Y-%m-%dT%H:%M:%S.%f%z'
        7:'%Y-%m-%dT%H:%M:%SZ'
        """
        if fmt == 0:
            date_time = parser.parse(date_time_str)
        else:
            date_time = datetime.strptime(date_time_str,cls.fmt_dict[fmt])

        if only_naive :
            assert cls.is_naive(date_time), "assert! date_time_str is not naive"

        return date_time

    @classmethod
    def from_stamp(cls, stamp:float, tz:Literal['KST','UTC']=None):
        stamp = cls._to_ten_digit(stamp)
        if tz is None:
            date_time = datetime.fromtimestamp(stamp)
        else:
            date_time = datetime.fromtimestamp(stamp, cls.tz_dict[tz])

        return date_time

    def _to_ten_digit(stamp_like:float):
        num_digits = len(str(int(stamp_like))) 
        print(num_digits)
        if num_digits <= 10:
            stamp = stamp_like
        else :
            divisor = 10 ** (num_digits - 10)
            stamp = stamp_like / divisor
        return stamp  
    
    def _stime_aware_to_naive(self,stime_aware:str, fmt:int=1):
        dtime_aware = self.from_str(stime_aware,fmt=0)
        dtime_naive = self.as_naive(dtime_aware)
        return self.to_str(dtime_naive, fmt)

    def _msg_from_to(self, dtime_stt, dtime_end, stype:Literal['full','short']):
        stt = datetime.strftime(dtime_stt,"%y.%m.%d %H:%M")
        if stype == 'full':
            end = datetime.strftime(dtime_end,"%y.%m.%d %H:%M")    
        else:
            end = datetime.strftime(dtime_end,"%H:%M")    
        return f"{stt} ~{end}"

if __name__ =="__main__":

    # ------------------------------------------------------------------------ #
    pytz.timezone('Asia/Seoul').localize(datetime(2020,10,10,0,0,0))
    datetime(2020,10,10,0,0,0,tzinfo=pytz.timezone('Asia/Seoul'))
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    #                                   init                                   #
    # ------------------------------------------------------------------------ #
    div = lambda x: print(f"{"="*60} [{x}]")
    typ = lambda x: print(type(x), x)
    timez = Timez()

    # ------------------------------------------------------------------------ #
    #                                    now                                   #
    # ------------------------------------------------------------------------ #
    div('datetime now timez')
    now_kst = timez.now('KST')
    now_utc = timez.now('UTC')
    typ(now_kst)
    typ(now_utc)

    # ------------------------------------------------------------------------ #
    #                                    to                                    #
    # ------------------------------------------------------------------------ #
    div('datetime to timez stamp')
    typ(timez.to_stamp(now_kst))
    typ(timez.to_stamp(now_utc))

    # ------------------------------------------------------------------------ #
    div('datetime to timez str')
    typ(timez.to_str(now_kst,1))
    typ(timez.to_str(now_utc,1))
    typ(timez.to_str(now_kst,3))
    typ(timez.to_str(now_utc,3))

    # ------------------------------------------------------------------------ #
    #                                    as                                    #
    # ------------------------------------------------------------------------ #
    div('datetime as naive')
    now_kst_nai = timez.as_naive(now_kst)
    now_utc_nai = timez.as_naive(now_utc)
    typ(now_kst_nai)
    typ(now_utc_nai)

    # ------------------------------------------------------------------------ #
    div('datetime as localize')
    typ(timez.as_localize(now_kst_nai,'KST'))
    typ(timez.as_localize(now_utc_nai,'UTC'))

    # ------------------------------------------------------------------------ #
    div('datetime as astimezone')
    typ(timez.as_timezone(now_utc,'KST'))
    typ(timez.as_timezone(now_kst,'UTC'))
    # ------------------------------------------------------------------------ #
  
    # ------------------------------------------------------------------------ #
    #                                   from                                   #
    # ------------------------------------------------------------------------ #
    # -------------------------------- string -------------------------------- #
    div('string from target')
    now = timez.now('UTC')
    typ(now)

    div('string from sample')
    typ(timez.to_str(now,1))
    typ(timez.to_str(now,2))
    typ(timez.to_str(now,3))
    typ(timez.to_str(now,4))
    typ(timez.to_str(now,5))
    typ(timez.to_str(now,6))

    div('parser-fmt1')
    typ(timez.from_str(timez.to_str(now,1),0))
    typ(timez.from_str(timez.to_str(now,1),1))

    div('parser-fmt2')
    typ(timez.from_str(timez.to_str(now,2),0))
    typ(timez.from_str(timez.to_str(now,2),2))

    div('parser-fmt3')
    typ(timez.from_str(timez.to_str(now,3),0))
    typ(timez.from_str(timez.to_str(now,3),3))

    div('parser-fmt4')
    typ(timez.from_str(timez.to_str(now,4),0))
    typ(timez.from_str(timez.to_str(now,4),4))

    div('parser-fmt5')
    typ(timez.from_str(timez.to_str(now,5),0))
    typ(timez.from_str(timez.to_str(now,5),5))

    div('parser-fmt6')
    typ(timez.from_str(timez.to_str(now,6),0))
    typ(timez.from_str(timez.to_str(now,6),6))

    # --------------------------------- stamp -------------------------------- #
    div('timestamp from target')
    now = timez.now()
    now_kst = timez.now(tz='KST')
    now_utc = timez.now(tz='UTC')
    typ(now)
    typ(now_kst)
    typ(now_utc)

    typ(timez.to_stamp(now))
    typ(timez.to_stamp(now_kst))
    typ(timez.to_stamp(now_utc))

    stamp = timez.to_stamp(now)
    div('timestamp from')

    typ(timez.from_stamp(stamp))
    typ(timez.from_stamp(stamp,tz='KST'))
    typ(timez.from_stamp(stamp,tz='UTC'))