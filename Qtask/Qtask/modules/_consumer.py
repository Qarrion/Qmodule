import time
from typing import Callable
from Qlogger import Logger
import asyncio
from Qtask.utils.custom_print import cprint
from Qtask.modules._producer import Core
from collections import namedtuple
Item = namedtuple('item', ['args', 'kwargs'])

class Consumer:

    def __init__(self, name:str='consumer', msg=False):
        self._logger = Logger(logname=name, clsname='Consumer', msg=msg, context='async')
        self.core = Core
        self.xwork = None
        self.queue = None
        self.fail = asyncio.Queue()
        self._status = 'stop'
        self.set_config()


    # ------------------------------------------------------------------------ #
    #                                  config                                  #
    # ------------------------------------------------------------------------ #    
    def set_config(self,timeout=None, msg_flow=True, msg_adjust=False, msg_item=False):
        self._timeout=timeout
        self._msg_flow=msg_flow
        self._msg_adjust=msg_adjust
        self._msg_item=msg_item
        
    def set_queue(self, queue:asyncio.Queue, msg=False):
        self.queue = queue
        if msg: self._logger.info.msg(queue._name,"","")

    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    def set_xwork(self, xdef:Callable, queue:asyncio.Queue=None, msg=False):
        """
        + arg 'channel' object should be assigned in the 'set_xwork' or 'set_channel'
        + msg for | xput_queue....item | 
        """
        self.xwork = xdef
        if msg : self._logger.info.msg(xdef.__name__,"",widths=(2,1))
        if queue is not None : self.set_queue(queue)
    
    # ------------------------------------------------------------------------ #
    #                                  consume                                 #
    # ------------------------------------------------------------------------ #
    async def xrun_queue(self, item:Item, timeout:int=None):
        # -------------------------------------------------------------------- #
        if self.is_starting():
            self.init_tsp = time.time()
            if self._msg_flow : self._logger.info.msg(self.xwork.__name__,
                widths=(3,),aligns=("<"),paddings=("-"),offset=self.core.offset)
        # -------------------------------------------------------------------- #
        try:
            if self._msg_item: self._logger.info.msg(f"{self.xwork.__name__}()",str(item))
            await asyncio.wait_for(self.xwork(*item.args, **item.kwargs), timeout=timeout) 

        except Exception as e:
            self._logger.warning.msg(
                f"{self.xwork.__name__}",f'except (fail)',e.__class__.__name__)
            await self.fail.put(item)

        finally:
            self.queue.task_done()
            # ---------------------------------------------------------------- #
            if self.is_stopping():
                sec = round(time.time() - self.init_tsp,3)
                if self._msg_flow : self._logger.info.msg(f"{self.xwork.__name__}[{sec}]",
                    widths=(3,),aligns=(">"),paddings=("-"),offset=self.core.offset)


    async def xconsume(self, timeout:int=None):
        assert self.xwork is not None
        while True:
            try:
                item = await self.queue.get()
                task = await self.xrun_queue(item, timeout)
                
            except asyncio.exceptions.CancelledError:
                task_name = asyncio.current_task().get_name()
                cprint(f"Interrupted ! loop_xconsume ({task_name}) closed",'yellow_')
                break      

            except Exception as e:
                raise e

    # ------------------------------------------------------------------------ #
    #                                   debug                                  #
    # ------------------------------------------------------------------------ #
    def is_starting(self):
        if self.queue._unfinished_tasks != 0 and self._status=='stop':
            self._status = 'start'
            return 1
        else:
            return 0
    def is_stopping(self):
        if self.queue._unfinished_tasks == 0 and self._status=='start':
            self._status = 'stop'
            return 1
        else:
            return 0


if __name__ == "__main__":
    from Qtask.modules._producer import Producer
    from Qtask.modules._consumer import Consumer
    queue = asyncio.Queue()
    prod = Producer(name='prod')
    
    prod.set_timer('every_seconds',5)
    prod.set_queue(queue)
    

    async def xprod():
        await prod.xput_queue(1)
        await prod.xput_queue(2,4)
        await prod.xput_queue(x=2,y=4)

    prod.set_xwork(xdef=xprod)
    # ------------------------------------------------------------------------ #
    cons = Consumer(name='cons')
    cons.set_queue(queue)
    
    async def xcons(x, y=2):
        print(f"consume {x=:},{y=:}")
        # raise
    cons.set_xwork(xdef=xcons)
    
    async def main():

        tasks =[
        asyncio.create_task(prod.xproduce()),
        asyncio.create_task(cons.xconsume()),
        ]    
        await asyncio.gather(*tasks)

    asyncio.run(main())