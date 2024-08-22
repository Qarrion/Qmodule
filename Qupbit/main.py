import asyncio
from re import U
from Qupbit import Market
from Qupbit import Candle
from Qupbit import Upbit
from Qupbit.utils.logger_color import ColorLog

if __name__ == "__main__":

    logger = ColorLog('upbit', 'green')

    # ------------------------------------------------------------------------ #
    #                                  market                                  #
    # ------------------------------------------------------------------------ #

    # market = Market(logger=logger)
    # market.valid()
    # rslt = market.get()
    # rslt.keys()
    
    # ------------------------------------------------------------------------ #
    #                                  candle                                  #
    # ------------------------------------------------------------------------ #
    
    candle = Candle()

    from datetime import datetime

    def get_now():
        return datetime.now()
    print(get_now())

    async def work():
        
        #last
        async with candle.xclient() as xclient:

            MKT = 'KRW-BTC'
            TGT = candle.to_last(get_now(),stime=True)
            print(TGT)

            rslt = await candle.xget(xclient=xclient,market=MKT,to=None, count=5,tz='KST',key=None)
            last = candle.to_last(rslt['time'])
            chek = candle.to_last(rslt['time'],stime=True)
            rows = candle.to_rows(rslt['payload'],key='namedtuple')

            # elif 


    async def main():
        await work()

    asyncio.run(main())
    # ------------------------------------------------------------------------ #
    #                                   upbit                                  #
    # ------------------------------------------------------------------------ #
    # upbit = Upbit(logger)

    # print(upbit.get_candle())
    # ------------------------------------------------------------------------ #
    # time
    from Qupbit.tools.timez import Timez

    timez = Timez()

    now_kst = timez.now('KST')
    now_utc = timez.now('UTC')


    now_kst.replace(tzinfo=None)
    now_kst

    timez.as_localize(now_kst, 'UTC')

    now_utc.replace(tzinfo=None)
    now_utc