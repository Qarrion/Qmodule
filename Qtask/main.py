

from multiprocessing import managers
from Qtask import Task
import asyncio

from Qtask.modules.consumer import consumer, producer
from Qtask.modules.limiter import Limiter

t_task = Task('worker')
t_task.set_timer('minute_at_seconds',10,'KST')

# async def pub():
#     for i in range(10):
        # await t_task.xput_channel(args=(i/10,))

async def pub():
    while True:
        await asyncio.sleep(10)
        await t_task.xput_channel(args=(5,),msg=True)

t_task.set_producer(pub)

async def sub(sec):
    await asyncio.sleep(sec)

t_task.set_consumer(sub)

async def main():
    p_task = asyncio.create_task(t_task.xrun_xproduce())
    c_task = asyncio.create_task(t_task.xrun_xconsume())

    await asyncio.gather(p_task, c_task)

asyncio.run(main())



producer
consumer
limiter
manager
broker
