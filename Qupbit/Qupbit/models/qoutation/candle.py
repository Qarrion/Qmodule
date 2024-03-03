import requests
from Qupbit.tools.parser import Parser
from Qupbit.tools.tracer import Tracer 
from Qupbit.models import info
import logging
from typing import List


class Candle:

	url_candle='https://api.upbit.com/v1/candles/minutes/1'
	headers = {"Accept": "application/json"}

	def __init__(self, logger:logging.Logger=None, debug=True):
		self.tracer = Tracer(logger)
		self.parser = Parser()
		self._debug = debug

	def get(self):
		"""status, header, payload, remain[group, min, sec], text"""
		resp = requests.get(url=self.url_candle, headers=self.headers, params=self.params)
		rslt = self.parser.response(resp)
		if self._debug : self.tracer.debug.request('candle',rslt['remain']) 
		return rslt		

if __name__=='__main__':
    from Qlogger import Logger
    logger = Logger('test','level')
    candle = Candle(logger)

    print('# ---------------------------------- get --------------------------------- #')
    rslt = candle.get()
    print(rslt.keys())

    print('# --------------------------------- test --------------------------------- #')
    candle.test(rslt,header=True, column=True)

    print('# -------------------------------- filter -------------------------------- #')
    rslt_filtered = candle.filter(rslt['payload'], market='KRW-BTC')
    print("KRW-BTC", len(rslt_filtered))
    print(rslt_filtered)

    rslt_filtered = candle.filter(rslt['payload'], qoute='KRW')
    print("qoute-KRW", len(rslt_filtered))

    rslt_filtered = candle.filter(rslt['payload'], base='BTC')
    print("base-BTC", len(rslt_filtered))