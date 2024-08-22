import re
import requests
from typing import List
from datetime import datetime
import pytz




class Parser():
     
    _re_remaining_req = re.compile(r"group=([\w-]+); min=([0-9]+); sec=([0-9]+)")
    _tz_kst = pytz.timezone('Asia/Seoul')
    _tz_gmt = pytz.timezone('GMT')

    def remaining(self, remaining_req):
        """resp.headers['Remaining-Req']"""
        remaining_req_dict = {}
        res_re = self._re_remaining_req.search(remaining_req)
        remaining_req_dict['group'] = res_re.group(1)
        remaining_req_dict['min'] = int(res_re.group(2))
        remaining_req_dict['sec'] = int(res_re.group(3))
        return remaining_req_dict
    
    def remaining_msg(self, remaining_req):
        res_re = self._re_remaining_req.search(remaining_req)
        return f"{res_re.group(1)}({res_re.group(3)}/s)"

    def response(self, resp:requests.Response)->dict:
        """status, header, payload, remain[group, min, sec], text"""
        
        response_dict = {}
        response_dict['status'] = resp.status_code
        response_dict['header'] = resp.headers
        response_dict['remain'] = self.remaining_msg(resp.headers['Remaining-Req'])
        # response_dict['remain'] = self.remaining(resp.headers['Remaining-Req'])
        response_dict['url'] = resp.url
        response_dict['time'] = self.header_date(resp.headers,None)
        
        if response_dict['status'] == 200:
            response_dict['payload'] = resp.json()  
            response_dict['text'] = None
        else :
            response_dict['payload'] = None
            response_dict['text'] = resp.text
        return response_dict
    
    def header_date(self, header, fallback=None):
        try:
            date_naive  = datetime.strptime(header['Date'], '%a, %d %b %Y %H:%M:%S GMT')
            date_gmt = self._tz_gmt.localize(date_naive)
            date_kst = date_gmt.astimezone(self._tz_kst)
        except Exception as e:
            print("header['Date] exception")
            print(header['Date'])
            if fallback is None:
                date_kst = pytz.timezone('Asia/Seoul')
            else:
                date_kst = fallback
        return date_kst

    def market(self, payload:List[dict], key, quote=None, base=None, market=None):
        """ >>> parser.market() 
        # list comprehension """
        if market is not None:
            payload = [d for d in payload if d[key] == market]

        if quote is not None:
            payload = [d for d in payload if d[key].startswith(quote)]

        if base is not None:
            payload = [d for d in payload if d[key].endswith(base)]
            
        return payload        
    
    def allkeys(self, nested_dict:dict):
        keys_list = []
        for key, value in nested_dict.items():
            keys_list.append(key)  # 현재 레벨의 키를 추가
            if isinstance(value, dict):
                keys_list.extend(self.allkeys(value))  # value가 딕셔너리일 경우, 재귀적으로 호출
        return keys_list
    
if __name__ =="__main__":
    from Zupbit.utils.custom_print import eprint
    from Zupbit.modules.market import Market
    market = Market()
    parser = Parser()
    rslt = market.get()
    
    # ------------------------------------------------------------------------ # 
    eprint('time')
    print(rslt['time'])
    print(datetime.now())

    # eprint('market')
    # print(parser.market(rslt['payload'], key='market', market='KRW-BTC'))
    # eprint('base')
    # print(parser.market(rslt['payload'], key='market', base='ETH')[0])
    # eprint('quote')
    # print(parser.market(rslt['payload'], key='market', quote='USDT')[0])
    
    # ------------------------------------------------------------------------ #
    # eprint('allkeys')
    # print(parser.allkeys(rslt['payload'][0]))