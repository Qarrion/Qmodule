from typing import Callable, Literal

from Qtask.modules.produce import Produce
from Qtask.modules.consume import Consume
from Qtask.modules.channel import Channel
from Qtask.modules.limiter import Limiter


class Task:

    def __init__(self,name):
        self.channel = Channel(name)
        self.consume = Consume(name)
        self.produce = Produce(name)

    # ------------------------------------------------------------------------ #
    #                                   prod                                   #
    # ------------------------------------------------------------------------ #
    def set_timer(self,
            every: Literal['minute_at_seconds', 'hour_at_minutes', 'day_at_hours',
                                    'every_seconds', 'every_minutes', 'every_hours'], 
            at: float = 5, tz: Literal['KST', 'UTC'] = 'KST', msg: bool = False):
        """+ timer on producer or preset"""
        self.produce.set_timer(every=every,at=at,tz=tz,msg=msg)

    def set_preset(self,preset: Literal['xsync_time', 'msg_divider']):
        """+ produce preset"""
        self.produce.set_preset(preset=preset)

    def set_producer(self,xdef:Callable):
        """+ produce"""
        channel = self.channel
        self.produce.set_producer(xdef=xdef, channel=channel)

    async def xput_channel(self,args:tuple=(), kwargs:dict=None, retry= 0, msg= False):
        await self.produce.xput_channel(args,kwargs,retry,msg)

    async def xrun_xproduce(self,xdef:Callable=None,timeout=None,msg=True):
        await self.produce.xproduce(xdef=xdef,timeout=timeout,msg=msg)

    # ------------------------------------------------------------------------ #
    #                                   cons                                   #
    # ------------------------------------------------------------------------ #
    def set_consumer(self,xdef:Callable):
        channel = self.channel
        self.consume.set_consumer(xdef=xdef, channel=channel)

    async def xrun_xconsume(self):
        await self.consume.xconsume()



if __name__ == "__main__":

    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    # import asyncio

    # t_task = Task('worker')
    # t_task.set_timer('every_seconds',10,'KST')
    
    # async def pub():
    #     for i in range(10):
    #         await t_task.xput_channel(args=(i/10,))

    # t_task.set_producer(pub)

    # async def sub(sec):
    #     await asyncio.sleep(sec)

    # t_task.set_consumer(sub)

    # async def main():
    #     p_task = asyncio.create_task(t_task.xrun_xproduce())
    #     c_task = asyncio.create_task(t_task.xrun_xconsume())

    #     await asyncio.gather(p_task, c_task)

    # asyncio.run(main())

    # ------------------------------------------------------------------------ #
    #                                  limiter                                 #
    # ------------------------------------------------------------------------ #
    import asyncio

    limit = Limiter('g_mkt')._set(5,1,'outflow')

    t_task = Task('worker')
    t_task.set_timer('every_seconds',10,'KST')
    
    async def pub():
        for i in range(10):
            await t_task.xput_channel(args=(i/10,),msg=False)

    t_task.set_producer(pub)

    async def sub(sec):
        await asyncio.sleep(sec)

    sub_lim = limit.wrapper(sub)

    t_task.set_consumer(sub_lim)

    async def main():
        p_task = asyncio.create_task(t_task.xrun_xproduce())
        c_task = asyncio.create_task(t_task.xrun_xconsume())

        await asyncio.gather(p_task, c_task)

    asyncio.run(main())