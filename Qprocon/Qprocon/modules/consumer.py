import time
import traceback
from typing import Callable, Literal
from Qlogger import Logger
import asyncio
from Qprocon.utils.custom_print import cprint
from Qprocon.modules.producer import Core
from collections import namedtuple
Item = namedtuple('item', ['args', 'kwargs', 'retry'])
class Consumer:

    def __init__(self, name:str='consumer', msg=False):
        self._logger = Logger(logname=name, clsname='Consumer', msg=msg, context='async')

        self.core = Core
        self.xworker = None
        self.queue = None
        self._status = 'stop'

        self._raise_in_drop = False
        self._msg_item = False


    def set_queue(self, queue:asyncio.Queue, msg=False):
        self.queue = queue
        if msg: self._logger.info.msg(queue._name,"","")

    # ------------------------------------------------------------------------ #
    #                                  worker                                  #
    # ------------------------------------------------------------------------ #
    def set_xworker(self, xdef:Callable, queue:asyncio.Queue=None, msg=False):
        """
        + arg 'channel' object should be assigned in the 'set_xworker' or 'set_channel'
        + msg for | xput_queue....item | 
        """
        self.xworker = xdef
        if msg : self._logger.info.msg(xdef.__name__,"",widths=(2,1))
        if queue is not None:
            self.set_queue(queue)

    async def xrun_queue(self,item:Item, timeout:int=None, maxtry=3, msg_flow=True):
        # -------------------------------------------------------------------- #
        if self.is_starting():
            self.init_tsp = time.time()
            if msg_flow : self._logger.info.msg(self.xworker.__name__,
                widths=(3,),aligns=("<"),paddings=("-"),offset=self.core.offset)
        # -------------------------------------------------------------------- #
        try:
            if self._msg_item: self._logger.info.msg(f"{self.xworker.__name__}()",str(item))
            await asyncio.wait_for(self.xworker(*item.args, **item.kwargs), timeout=timeout) 

        except Exception as e:
            if item.retry < maxtry:
                new_item = item._replace(retry=item.retry+1)
                self._logger.warning.msg(
                    f"{self.xworker.__name__}()",f'except (retry {new_item.retry})',e.__class__.__name__)
                await self.queue.put(new_item)
            else:
                self._logger.error.msg(
                    f"{self.xworker.__name__}()",f'except (drop)',e.__class__.__name__,debug_var='raise_in_drop')
                if self._raise_in_drop:
                    # traceback.print_exc()
                    raise e    

        finally:
            self.queue.task_done()
            # ---------------------------------------------------------------- #
            if self.is_stopping():
                sec = round(time.time() - self.init_tsp,3)
                if msg_flow : self._logger.info.msg(f"{self.xworker.__name__}[{sec}]",
                    widths=(3,),aligns=(">"),paddings=("-"),offset=self.core.offset)
            # ---------------------------------------------------------------- #

    async def xconsume(self, timeout:int=None, maxtry:int=3, raise_in_drop=False, msg_flow=False, msg_item=False):
        self._raise_in_drop = raise_in_drop
        self._msg_item = msg_item
        assert self.xworker is not None
        while True:
            try:
                item = await self.queue.get()
                task = await self.xrun_queue(item, timeout,maxtry, msg_flow=msg_flow)
                
            except asyncio.exceptions.CancelledError:
                task_name = asyncio.current_task().get_name()
                cprint(f"Interrupted ! loop_xconsume ({task_name}) closed",'yellow_')
                break      

            except Exception as e:
                if self._raise_in_drop:
                    self._logger.error.msg(f"{self.xworker.__name__}()",f'except (exit task)',
                                           e.__class__.__name__,debug_var='raise_in_drop')
                    traceback.print_exc()
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
    queue = asyncio.Queue()
    from Qprocon.modules.producer import Producer
    # ------------------------------- producer ------------------------------- #
    prod = Producer(name='prod')

    prod.set_timer('every_seconds',5)
    prod.set_queue(queue)

    async def xprod():
        await prod.xput_queue(args=(1,))
        await prod.xput_queue(args=(2,4))
        await prod.xput_queue(kwargs=dict(x=2,y=4))

    prod.set_xworker(xdef=xprod)


    # ------------------------------- consumer ------------------------------- #
    cons = Consumer(name='cons')
    cons.set_queue(queue)

    async def xcons(x, y=2):
        print(f"consume {x=:},{y=:}")
        # raise
    cons.set_xworker(xdef=xcons)

    async def main():

        tasks =[
        asyncio.create_task(prod.xproduce(msg_flow=True, msg_item=True)),
        asyncio.create_task(cons.xconsume(msg_flow=True)),
        ]    

        await asyncio.gather(*tasks)

    asyncio.run(main())