import re

class Parser():
     
    re_remaining_req = re.compile("group=([\w-]+); min=([0-9]+); sec=([0-9]+)")

    def remaining_req(self, remaining_req):
        remaining_req_dict = {}
        res_re = self.re_remaining_req.search(remaining_req)
        remaining_req_dict['group'] = res_re.group(1)
        remaining_req_dict['min'] = int(res_re.group(2))
        remaining_req_dict['sec'] = int(res_re.group(3))

        return remaining_req_dict
