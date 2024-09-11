# -------------------------------- ver 202409 -------------------------------- #
# _prod_only in 'preset', 'set_xproduce'

import asyncio
from socket import timeout
from typing import Literal
from Qtask.modules._consumer import Consumer
from Qtask.modules._producer import Producer
from Qlogger import Logger



class Pulser:
    
    def __init__(self, name:str='timer'):
        self._logger = Logger(logname=name, clsname='Timer')
        self._name = name
        self.cons = Consumer(name='cons')
        self.prod = Producer(name='prod')
        
        self._logger.set_sublogger(self.cons._logger)
        self._logger.set_sublogger(self.prod._logger)
        
        self.queue = asyncio.Queue()
        self.cons.set_queue(self.queue,msg=False)
        self.prod.set_queue(self.queue,msg=False)
    
        self.set_config()
    
        self._prod_only = False # preset
    
    def set_config(self, timeout=None, msg_flow=False, msg_adjust=False, msg_item=False):
        self.cons.set_config(timeout=timeout,msg_flow=msg_flow, msg_adjust=msg_adjust,msg_item=msg_item)
        self.prod.set_config(timeout=timeout,msg_flow=msg_flow, msg_adjust=msg_adjust,msg_item=msg_item)
        
        
    def now_kst(self, msg=False):
        return self.prod._nowst.now_kst(msg=msg)
    
    # ------------------------------------------------------------------------ #
    #                                 producer                                 #
    # ------------------------------------------------------------------------ #
    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes',
                    'day_at_hours','every_seconds','every_minutes','every_hours'], 
                    at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        self.prod.set_timer(every=every,at=at,tz=tz,msg=msg)
        
    def set_preset(self, preset:Literal['xsync_time','msg_divider','xput_default'],msg_xsync=True):
        self.prod.set_preset(preset=preset, msg_xsync=msg_xsync)
        if preset in ['xsync_time','msg_divider']:
            self._prod_only = True
            
    async def xput_item(self, *args,  **kwargs):
        await self.prod.xput_queue(*args, **kwargs)
        
    def get_partial(self, func, *args, **kwargs):
        return self.prod.get_partial(func, *args, **kwargs)
    
    def set_xproducer(self,xdef, prod_only=False):
        self.prod.set_xwork(xdef=xdef)
        if prod_only:
            self._prod_only=True
        
    # ------------------------------------------------------------------------ #
    #                                 consumer                                 #
    # ------------------------------------------------------------------------ #
    def set_xconsumer(self, xdef):
        self.cons.set_xwork(xdef=xdef)
        
        
    # --------------------------------- start -------------------------------- #
    async def pulser_gather(self, timeout:int =None, test=False):
        tasks = []
        task_prod = asyncio.create_task(
            self.prod.xproduce(test=test), name=f"{self._name}-p")
        tasks.append(task_prod)
        
        if not self._prod_only:
            task_cons = asyncio.create_task(
                self.cons.xconsume(timeout=timeout), name=f"{self._name}-c")
            tasks.append(task_cons)
        
        await asyncio.gather(*tasks)
 
    def pulser_task(self, timeout:int =None, test=False):
        tasks = []
        task_prod = asyncio.create_task(
            self.prod.xproduce(test=test), name=f"{self._name}-p")
        tasks.append(task_prod)
        
        if not self._prod_only:
            task_cons = asyncio.create_task(
                self.cons.xconsume(timeout=timeout), name=f"{self._name}-c")
            tasks.append(task_cons)
        
        return asyncio.gather(*tasks)
        
if __name__ == "__main__":
    timer = Pulser()
    timer.set_timer('every_seconds',5)
    async def xdef():
        await timer.xput_item(1,2)
    timer.set_xproducer(xdef)
    
    async def xprint(x,y):
        print(x, y)
    timer.set_xconsumer(xprint)
    
    async def main():
        task = asyncio.create_task(timer.pulser_gather())
        await task
        
    async def main():
        task = timer.pulser_task()
        await task
        
    asyncio.run(main()) 