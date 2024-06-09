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
            TGT = candle.chk_time(get_now(),chk=True)
            print(TGT)

            rslt = await candle.xget(xclient=xclient,market=MKT,to=None, count=5,tz='KST',key=None)
            last = candle.chk_time(rslt['time'])
            chek = candle.chk_time(rslt['time'],chk=True)
            rows = candle.to_rows(rslt['payload'],key='namedtuple')

            print(chek)
            print(pd.DataFrame(rslt['payload']))

            if rows[0].time == last.trade:
                print('case 1 : upload rows[1] : 정상')

            # elif 


    async def main():
        await work()

    asyncio.run(main())
    # ------------------------------------------------------------------------ #
    #                                   upbit                                  #
    # ------------------------------------------------------------------------ #
    upbit = Upbit(logger)

    print(upbit.get_candle())