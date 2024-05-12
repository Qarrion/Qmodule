from ast import Call
from typing import Callable, Literal

from Qtask.modules.produce import Produce
from Qtask.modules.consume import Consume
from Qtask.tools.taskq import TaskQue
from Qtask.tools.limit import Limiter


class Task:

    def __init__(self,name):
        self.consume = Consume(name)
        self.produce = Produce(name)

    # def __init__(self, consume='consume',produce='produce',limiter='limiter'):
        # self.consume = Consume(consume)
        # self.produce = Produce(produce)
        # self.limiter = RateLimit(limiter)

    # ------------------------------------------------------------------------ #
    #                                   task                                   #
    # ------------------------------------------------------------------------ #
    # def set_taskque(self, name):
    #     """named singleton"""
    #     self.taskque['name'] = TaskQue(name)

    # def task_set_taskque(self, name):
    #     """singleton"""
    #     self.consume.set_taskque(name)
    #     self.produce.set_taskque(name)

    # ------------------------------------------------------------------------ #
    #                                   rate                                   #
    # ------------------------------------------------------------------------ #
    def rate_get_limiter(self, 
            max_worker: int, seconds: float, limit: Literal['inflow', 'outflow', 'midflow']):
        self.limiter.set_rate(max_worker, )

    # ------------------------------------------------------------------------ #
    #                                   prod                                   #
    # ------------------------------------------------------------------------ #
    def prod_set_timer(self,
            every: Literal['minute_at_seconds', 'hour_at_minutes', 'day_at_hours',
                                    'every_seconds', 'every_minutes', 'every_hours'], 
            at: float = 5, tz: Literal['KST', 'UTC'] = 'KST', msg: bool = False):
        self.produce.set_timer(every=every,at=at,tz=tz,msg=msg)

    def prod_set_preset(self,preset: Literal['xsync_time', 'msg_divider']):
        self.produce.set_preset(preset=preset)

    def prod_set_producer(self,async_def:Callable, fname:str = None):
        self.produce.set_producer(async_def=async_def,fname=fname)

    async def prod_xput_taskque(self,fname:str, args:tuple=(), kwargs:dict=None, 
                                timeout:int=None, retry: int = 0, msg: bool = True):
        await self.produce.xput_taskque(fname=fname,args=args,kwargs=kwargs,
                                                timeout=timeout,retry=retry,msg=msg)

    async def prod_xrun_xproduce(self,async_defs:Callable=None,timeout=None,msg=True):
        await self.produce.xproduce(async_defs=async_defs,timeout=timeout,msg=msg)

    # ------------------------------------------------------------------------ #
    #                                   cons                                   #
    # ------------------------------------------------------------------------ #
    def cons_set_taskque(self, taskque:TaskQue):
        self.consume.set_taskque(taskque)

    def cons_set_consumer(self,async_def:Callable,fname: str = None):
        self.consume.set_consumer(async_def=async_def, fname=fname)

    async def cons_xrun_xconsume(self,msg=True):
        await self.consume.xconsume(msg=msg)

if __name__ == "__main__":
    import asyncio
    t_sync = Task('preset')
    t_sync.prod_set_timer('minute_at_seconds',55,'KST',False)
    t_sync.prod_set_preset('xsync_time')

    t_edev = Task('preset')
    t_edev.prod_set_timer('minute_at_seconds',59,'KST',False)
    t_edev.prod_set_preset('msg_divider')

    # ------------------------------------------------------------------------ #
    #                                prod + cons                               #
    # ------------------------------------------------------------------------ #
    # --------------------------------- prod --------------------------------- #
    t_task = Task('worker')
    t_task.prod_set_timer('minute_at_seconds',0,'KST')

    q_task = TaskQue('taskq')
    async def pub():
        for i in range(10):
            await q_task.xput_queue(fname='sub',args=(i/10,),msg=True)
            # await t_task.prod_xput_taskque(fname='sub',args=(i/10,))

    t_task.prod_set_producer(pub)
    # --------------------------------- cons --------------------------------- #
    t_task.cons_set_taskque(q_task)

    # -------------------------------- limiter ------------------------------- #
    limiter = Limiter('proc')
    limiter.set_rate(5,1,'inflow')
    async def proc(sec):
        await asyncio.sleep(sec)
    wproc = limiter.wrapper(proc)

    #TODO
    async def sub(sec):
        await wproc(sec)

    # -------------------------------- limiter ------------------------------- #
    t_task.cons_set_consumer(sub)

    async def main():
        p_sync = asyncio.create_task(t_sync.prod_xrun_xproduce(msg=False))
        p_edev = asyncio.create_task(t_edev.prod_xrun_xproduce(msg=False))
        p_task = asyncio.create_task(t_task.prod_xrun_xproduce())
        await asyncio.gather(p_sync,p_edev,p_task)
        # c_task = asyncio.create_task(t_task.cons_xrun_xconsume())
        # await asyncio.gather(p_sync,p_edev,p_task,c_task)

    asyncio.run(main())