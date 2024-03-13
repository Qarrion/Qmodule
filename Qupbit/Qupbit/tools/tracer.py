import logging
from typing import Literal
from Qupbit.utils.log_custom import CustomLog



class Tracer(CustomLog):
    
    def __init__(self, logger: logging.Logger, context: Literal['sync', 'thread', 'async'] = 'sync'):
        super().__init__(logger, context)

    def request(self, model, resp_dict):
        """debug : status = 200
        error : status != 200"""
        remain = resp_dict['remain']
        status = resp_dict['status']
        if status == 200:
            self.debug.args(model, remain['group']+"/g", f"{remain['min']}/m",f"{remain['sec']}/s",n_back=2)
        else:
            self.error.text(model, resp_dict['text'])

    def alert(self, text):
        self.warning.text('warning',text)

    def cols_match(self,model, is_cols_not_in_keys:list):
        self.text(model, f"cols ({', '.join(is_cols_not_in_keys)}) not in market")

    def test_header(self,model, name, value, test):
        self.args(model, name, value, test, n_back=2)

    def test_column(self,model, change, cols:list):
        if cols:
             self.text(model,f"cols ({', '.join(cols)}) {change}",n_back=2 )
        else:
            self.args(model, 'column', change, True,n_back=2)
       

# if __name__ == "__main__":
#     t = Tracer()