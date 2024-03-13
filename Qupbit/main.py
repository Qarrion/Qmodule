from Qupbit import Market



if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('market', 'head')
    market = Market(logger=logger)
    market.valid()
    rslt = market.get()
    rslt.keys()
    