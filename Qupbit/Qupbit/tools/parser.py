import re
import requests
from typing import List

class Parser():
     
    _re_remaining_req = re.compile(r"group=([\w-]+); min=([0-9]+); sec=([0-9]+)")

    def remaining(self, remaining_req):
        """resp.headers['Remaining-Req']"""
        remaining_req_dict = {}
        res_re = self._re_remaining_req.search(remaining_req)
        remaining_req_dict['group'] = res_re.group(1)
        remaining_req_dict['min'] = int(res_re.group(2))
        remaining_req_dict['sec'] = int(res_re.group(3))
        return remaining_req_dict

    def response(self, resp:requests.Response)->dict:
        """status, header, payload, remain[group, min, sec], text"""
        response_dict = {}
        response_dict['status'] = resp.status_code
        response_dict['header'] = resp.headers
        response_dict['remain'] = self.remaining(resp.headers['Remaining-Req'])
        response_dict['url'] = resp.url
        
        if response_dict['status'] == 200:
            response_dict['payload'] = resp.json()  
            response_dict['text'] = None
        else :
            response_dict['payload'] = None
            response_dict['text'] = resp.text
        return response_dict
    
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
    from Qupbit.utils.logger_color import ColorLog 
    from Qupbit.models import Market
    from Qupbit.utils.print_divider import eprint
    logger = ColorLog('test', 'blue')
    market = Market(logger, debug=True)
    parser = Parser()
    rslt = market.get()
    
    # ------------------------------------------------------------------------ # 
    eprint('market')
    print(parser.market(rslt['payload'], key='market', market='KRW-BTC'))
    eprint('base')
    print(parser.market(rslt['payload'], key='market', base='BTC'))
    eprint('quote')
    print(parser.market(rslt['payload'], key='market', quote='USDT'))
    
    # ------------------------------------------------------------------------ #
    eprint('allkeys')
    print(parser.allkeys(rslt['payload'][0]))