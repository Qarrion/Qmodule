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
    #                                   upbit                                  #
    # ------------------------------------------------------------------------ #
    upbit = Upbit(logger)

    print(upbit.get_candle())