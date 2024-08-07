# -------------------------------- ver 240518 -------------------------------- #
# to_rows: namedtuple
# ---------------------------------------------------------------------------- #

# https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
import asyncio
from re import T
from Qupbit.utils.logger_custom import CustomLog
from Qupbit.tools.valider import Valider
from Qupbit.tools.parser import Parser
from typing import List, Literal
import requests, httpx
from collections import namedtuple


# from Qupbit.tools.tracer import Tracer 

"""
Quote-Base
KRW-BTC (원화마켓 Bitcoin)
"""

Row = namedtuple('Market',['market','korean_name','english_name','market_warning','note'])
class Market:
    """ >>> # sync
    market = Market()
    rslt = market.get()
    cols = market.columns
    rows = market.to_rows(payload=rslt['payload'])
    
    >>> # asyncio
    async def main():
        async with market.xclient() as client:
            rslt = await market.xget(client)
            print(rslt['payload'][0])

    asyncio.run(main())
    """

    url_market = "https://api.upbit.com/v1/market/all"
    headers = {"Accept": "application/json"}
    params = {"isDetails": 'true'}


    # columns = ['market','korean_name','english_name','market_warning','last_updated']
    
    def __init__(self,name:str='market',msg=True):
        CLSNAME = 'Market'
        try:    
            from Qlogger import Logger
            logger = Logger(name,'head')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        self.valider = Valider(logger)
        self.parser = Parser()
        self.row_market = Row


    def get(self, session:requests.Session=None, key:Literal['status','header','payload','remain','text']=None, msg=False):
        """ >>> # return result
        if session is None:
            resp = requests.get()
        else:
            resp = session.get()
        """
        if session is None:
            resp = requests.get(url=self.url_market, headers=self.headers, params=self.params)
        else:
            resp = session.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self.parser.response(resp)
        # -------------------------------------------------------------------- #
        if rslt['status'] == 200:
            remain = rslt['remain']
            if msg : self._custom.info.msg("ALL", remain['group']+"/g",f"{remain['sec']}/s")
        else:
            self._custom.error.msg('ALL', f"code({rslt['status']})", "x/s")  
        # -------------------------------------------------------------------- #
        if key is not None: rslt = rslt[key]
        resp.raise_for_status()
        return rslt
    
    async def xget(self, xclient:httpx.AsyncClient=None, key:Literal['status','header','payload','remain','text']=None, msg=False):
        """
        >>> # 
        async with market.xclient() as xclient:
            rslt = await market.xget(xclient)        
        """
        is_context = False
        if xclient is None:
            xclient = httpx.AsyncClient()
            is_context = True

        resp = await xclient.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt = self.parser.response(resp)
        # -------------------------------------------------------------------- #
        if rslt['status'] == 200:
            remain = rslt['remain']
            if msg : self._custom.info.msg("ALL", remain['group']+"/g",f"{remain['sec']}/s")
        else:
            self._custom.error.msg('ALL', f"code({rslt['status']})", "x/s")  
        # -------------------------------------------------------------------- #
            
        if key is not None: rslt = rslt[key]
        if is_context : await xclient.aclose()
        resp.raise_for_status()
        return rslt

    def to_rows(self,payload:List[dict], quote=None, base=None, market=None, key:Literal['tuple','namedtuple']='tuple'):
        """ >>> market.to_rows(result['payload']) 
        # market, korean_name, english_name, market_warning """
        selected_payload = self.parser.market(payload,'market', quote, base, market)
        selected_rows =[
            (
                d['market'], d['korean_name'], d['english_name'],
                d['market_event']['warning'],
                # d['market_event']['caution']['PRICE_FLUCTUATIONS'],
                # d['market_event']['caution']['TRADING_VOLUME_SOARING'],
                # d['market_event']['caution']['DEPOSIT_AMOUNT_SOARING'],
                # d['market_event']['caution']['GLOBAL_PRICE_DIFFERENCES'],
                # d['market_event']['caution']['CONCENTRATION_OF_SMALL_ACCOUNTS']
                'fetch'
            ) 
                for d in selected_payload
        ]
        if key=='namedtuple':
            
            selected_rows = [Row(*item) for item in selected_rows]
        return selected_rows
    
    def to_dict(self, row:Row):
        if isinstance(row, Row):
            return row._asdict()
        else:
            print(f"\033[31m row is not instance Row({Row.index} \033[0m")
        
    def _msg_result(self, status, result:dict, frame:str):
        remain = result['remain']
        if result['status'] == 200:
            self._custom.info.msg(status, remain['group']+"/g",f"{remain['sec']}/s", frame=frame)
        else:
            self._custom.error.msg(status, f"code({result['status']})", "e/s", frame=frame)    

if __name__=='__main__':
    from Qupbit.utils.print_divider import eprint

    
    market = Market()

    # ---------------------------------- get --------------------------------- #
    # eprint('get1')
    # rslt = market.get(msg=True)
    # # print(rslt)
    # # print(rslt.keys())
    # # eprint('payload')
    # # print(rslt['payload'][0:5])
    
    # eprint('get2')
    # rslt = market.get(None, 'payload')
    # eprint('rows')
    # rows = market.to_rows(payload=rslt)
    # print(rows[0:5])

    # --------------------------------- async -------------------------------- #

    async def main():
        async with httpx.AsyncClient() as xclient:
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            rslt = await market.xget(xclient,msg=True)
            print(rslt['payload'][0])

    asyncio.run(main())