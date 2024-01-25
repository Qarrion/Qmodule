from Qupbit.api import Market
from Qupbit.api import WebsocketClient
# from Qupbit.api import market

# # print(market.get())

# from Qupbit import upbit

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test', 'head')
    market = Market(logger)

    rslt = market.get()
    # print(rslt.keys())
    print(rslt['payload'])
