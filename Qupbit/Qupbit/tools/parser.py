import re
import requests
from typing import List

class Parser():
     
    _re_remaining_req = re.compile("group=([\w-]+); min=([0-9]+); sec=([0-9]+)")

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
        
        if response_dict['status'] == 200:
            response_dict['payload'] = resp.json()  
            response_dict['remain'] = self.remaining(resp.headers['Remaining-Req'])
            response_dict['text'] = None
        else :
            response_dict['payload'] = None
            response_dict['remain'] = None
            response_dict['text'] = resp.text
        return response_dict
    
    def response_market(self, payload:List[dict], key, qoute=None, base=None, market=None):
        
        if market is not None:
            payload = [d for d in payload if d[key] == market]

        if qoute is not None:
            payload = [d for d in payload if d[key].startswith(qoute)]

        if base is not None:
            payload = [d for d in payload if d[key].endswith(base)]
            
        return payload        
    
    def response_allkeys(self, nested_dict:dict):
        keys_list = []
        for key, value in nested_dict.items():
            keys_list.append(key)  # 현재 레벨의 키를 추가
            if isinstance(value, dict):
                keys_list.extend(self.response_allkeys(value))  # value가 딕셔너리일 경우, 재귀적으로 호출
        return keys_list