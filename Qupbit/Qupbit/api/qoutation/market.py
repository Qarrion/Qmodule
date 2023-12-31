import requests
from Qupbit.utils.config import Config
from Qupbit.tools import parser

config = Config('limit.ini', 'config', debug=True)
config.read_project('config')
config.is_section('rest-default')
# C:\Qarrion\Code\Qmodule\Qupbit\Qupbit\config\limit.ini


"""Quote-Base"""
class Market:
    """ test """
    url_market = "https://api.upbit.com/v1/market/all"
    params = {"isDetails": 'true'}
    headers = {"Accept": "application/json"}
    
    # def __init__(self):

    def get(self):
        """ >>> # Quote-Base 
        rslt = market.get()
        rslt['status']
        rslt['remain']
        rslt['payload'] """
        rslt = dict()
        resp = requests.get(url=self.url_market, headers=self.headers, params=self.params)
        rslt['status'] = resp.status_code

        if rslt['status'] == 200:
            rslt['remain'] = parser.remaining_req(resp.headers['Remaining-Req'])
            rslt['payload'] = resp.json()
        else:
            rslt['remain'] = None
            rslt['payload'] = None

        return rslt 
    
    def response(self):
        return requests.get(url=self.url_market, headers=self.headers, params=self.params)

    def filter(self, payload, qoute=None, base=None, market=None):
        if market is not None:
            rslt = [d for d in payload if d['market'] == market]
        elif qoute is not None:
            rslt = [d for d in payload if d['market'].startswith(qoute)]
        elif base is not None:
            rslt = [d for d in payload if d['market'].endswith(base)]
        return rslt
    
if __name__=='__main__':
    from datetime import datetime
    import time
    market = Market()

    # rslt = market.get()
    # rslt_filtered = market.filter(rslt['payload'], qoute='KRW')
    # rslt_filtered = market.filter(rslt['payload'], base='BTC')
    # rslt_filtered = market.filter(rslt['payload'], market='KRW-BTC')

    while True:
        rslt = market.get()
        current_time_gmt = datetime.utcnow()
        formatted_time = current_time_gmt.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{rslt['status']}] {formatted_time} {rslt['remain']}")
        time.sleep(0.1)