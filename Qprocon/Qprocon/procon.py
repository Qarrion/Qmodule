from ast import arg
import asyncio
from re import T
from typing import Literal
from Qprocon.modules.consumer import Consumer
from Qprocon.modules.producer import Producer
from Qlogger import Logger

"""
xrun : test (option)
"""

class Procon:

    def __init__(self, name:str='procon', msg=False):
        self._logger = Logger(logname=name, clsname='Procon', msg=msg, context='async')
        self._name = name
        self.cons = Consumer(name='cons')
        self.prod = Producer(name='prod')

        self._logger.set_sublogger(self.cons._logger)
        self._logger.set_sublogger(self.prod._logger)

        self.queue = asyncio.Queue()
        self.cons.set_queue(self.queue,msg=False)
        self.prod.set_queue(self.queue,msg=False)

    def now_kst(self, msg=False):
        return self.prod._nowst.now_kst(msg=msg)

    # ------------------------------------------------------------------------ #
    #                                 producer                                 #
    # ------------------------------------------------------------------------ #
    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                        'every_seconds','every_minutes','every_hours'], 
                    at:float=5, tz:Literal['KST','UTC']='KST',msg=False):
        self.prod.set_timer(every=every,at=at,tz=tz,msg=msg)

    def set_preset(self, preset: Literal['xsync_time', 'msg_divider']):
        self.prod.set_preset(preset=preset)

    async def xput_item(self, args:tuple=(), kwargs:dict={}, retry:int=0):
        await self.prod.xput_queue(args=args,kwargs=kwargs,retry=retry)
        
    def set_xproducer(self, xdef=None, args:tuple=None, kwargs:dict=None, msg=False):
        if xdef is None:
            if args is None:
                args = tuple()
            if kwargs is None:
                kwargs = dict()
            
            async def xdef():
                await self.xput_item(args=args, kwargs=kwargs)

        self.prod.set_xworker(xdef=xdef, msg=msg)

    def get_partial(self, func, *args, **kwargs):
        return self.prod.get_partial(func, *args, **kwargs)

    # ------------------------------------------------------------------------ #
    #                                 consumer                                 #
    # ------------------------------------------------------------------------ #
    def set_xconsumer(self, xdef, msg=False):
        self.cons.set_xworker(xdef=xdef, msg=msg)

    # ------------------------------------------------------------------------ #
    #                                    run                                   #
    # ------------------------------------------------------------------------ #
    async def xrun(self, timeout:int =55,  maxtry:int=3, raise_in_drop=False, test=False,
        msg_flow_cons=True, msg_flow_prod=False, msg_adjust=False, msg_item=False):
        
        task_prod = asyncio.create_task(
            self.prod.xproduce(timeout=timeout, test=test, msg_flow=msg_flow_prod, 
                msg_adjust=msg_adjust, msg_item=msg_item), name=f"prod")
        
        task_cons = asyncio.create_task(
            self.cons.xconsume(timeout=timeout, maxtry=maxtry, msg_flow=msg_flow_cons,
                raise_in_drop=raise_in_drop, msg_item=msg_item), name=f"cons")
        
        await asyncio.gather(task_prod,task_cons)

    # ------------------------------------------------------------------------ #
    async def xrun_pord(self, timeout:int =50, 
        test=False, msg_flow_prod=False, msg_adjust=False, msg_item=False):
        
        task_prod = asyncio.create_task(
            self.prod.xproduce(timeout=timeout, test=test, msg_flow=msg_flow_prod, 
                msg_adjust=msg_adjust, msg_item=msg_item), name=f"prod")
        
        await asyncio.gather(task_prod)

if __name__ == "__main__":

    procon = Procon()
    procon.set_timer('every_seconds',5)
    procon.set_xproducer(kwargs={'sec':1})
    # t_task.set_xproducer(args=(1,))

    async def sub(sec):
        # print(f"sub {sec} start")
        await asyncio.sleep(sec)
        raise ValueError
        # print(f"sub {sec} finish")

    procon.set_xconsumer(sub)

    async def main():
        task = asyncio.create_task(procon.xrun(
            msg_flow_cons=True, msg_flow_prod=True, msg_item=False, raise_in_drop=False))
        await asyncio.gather(task)

    asyncio.run(main())

