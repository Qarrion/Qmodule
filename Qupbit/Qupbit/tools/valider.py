# ---------------------------------------------------------------------------- #
#                https://docs.upbit.com/docs/user-request-guide                #
# ---------------------------------------------------------------------------- #
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.tools.parser import Parser
from typing import Literal
import logging

qoutation = dict()

# ---------------------------------- market ---------------------------------- #
qoutation['market']=dict()
qoutation['market']['group'] = 'market'
qoutation['market']['sec'] = 10
qoutation['market']['columns']=[
	'market', 'korean_name', 'english_name', 'market_warning', 'market_event', 'warning',
	'caution', 'PRICE_FLUCTUATIONS', 'TRADING_VOLUME_SOARING', 'DEPOSIT_AMOUNT_SOARING',
	'GLOBAL_PRICE_DIFFERENCES', 'CONCENTRATION_OF_SMALL_ACCOUNTS']
# ---------------------------------- candles ---------------------------------- #
qoutation['candles']=dict()
qoutation['candles']['group'] = 'candles'
qoutation['candles']['sec'] = 10
qoutation['candles']['columns']=[
	'market','candle_date_time_utc','candle_date_time_kst','opening_price',  
	'high_price','low_price','trade_price','timestamp','candle_acc_trade_price', 
	'candle_acc_trade_volume','unit']


class Valider:
	def __init__(self, logger:logging.Logger):
		self.parser = Parser()
		self.custom = CustomLog(logger,'async')

	def check(self, group:Literal['market','candles'], 
		   rslt, header=True, column=True):
		
		if header:
			"""group, remain 값 변동확인"""
			grp = qoutation[group]['group'] == rslt['remain']['group']
			sec = qoutation[group]['sec'] == rslt['remain']['sec']+1

			self.custom.debug.msg(group,'group',rslt['remain']['group'],grp)
			self.custom.debug.msg(group,'sec', rslt['remain']['sec']+1,sec)

		if column:
			"""response.json 의 keys 변동확인"""
			rslt_keys = self.parser.allkeys(rslt['payload'][0])
			info_keys = qoutation[group]['columns']
			add = [r for  r in rslt_keys if r not in info_keys]
			rmv = [i for  i in info_keys if i not in rslt_keys]

			self.custom.debug.msg('added', str(add))
			self.custom.debug.msg('removed',str(rmv))

if __name__ =="__main__":
	from Qupbit.utils.print_divider import eprint
	from Qupbit.utils.logger_color import ColorLog
	logger = ColorLog('test', 'green')
	valider = Valider(logger)

	# --------------------------------------------------------------------------- #
	eprint('market')
	from Qupbit.models import Market
	market = Market()
	rslt = market.get()
	valider.check('market',rslt)
		
	# --------------------------------------------------------------------------- #
	eprint('candles')
	from Qupbit.models import Candle
	candle = Candle()
	rslt = candle.get('KRW-BTC','2020-10-10T00:00:00',10,'KST')
	valider.check('candles',rslt) 