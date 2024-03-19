import logging
from typing import Literal, Coroutine

from functools import partial

import asyncio
from Qrepeater.timer import Timer
from Qrepeater.msg import Msg


class Repeater:
    
    def __init__(self, value:float, unit:Literal['second','minute','hour'], logger:logging.Logger):
        self.msg = Msg(logger, 'async')
        self.timer = Timer(value, unit, self.msg)

        self._stop_event = asyncio.Event()
        self._jobs = list()

    def register(self, func:Coroutine, args:tuple=(), kwargs:dict=None, timeout:float=None):
        self._jobs.append(partial(self._wrapper_job, func, args, kwargs, timeout))


    async def run(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.timer.remaining_seconds())
            async with asyncio.TaskGroup() as tg:
                for i, job in enumerate(self._jobs):
                    tg.create_task(job(),name = f'repeater-{i}')
            
    async def _wrapper_job(self,func:Coroutine, args:tuple=(), kwargs:dict=None, timeout:float=None):
        self.msg.job('start',func.__name__)
        if kwargs is None: kwargs={}
        if timeout is not None:
            try:                            #! execution
                await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:    #! timeout 
                self.msg.warning.exception(func.__name__, args, timeout)
        else:
            await func(*args, **kwargs)
        self.msg.info.job('finish',func.__name__)

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('main','head')

    # -------------------------------- asyncio ------------------------------- #
    async def myfunc(x):
        await asyncio.sleep(x)

    async def main():
        repeater = Repeater(value=10, unit='second', logger=logger)

        repeater.register(myfunc,(6,),timeout=8)
        repeater.register(myfunc,(9,),timeout=8)
        repeater.register(myfunc,(12,),timeout=8)

        await repeater.run()

    asyncio.run(main())

# ---------------------------------------------------------------------------- #

    # await asyncio.sleep(self.timer.remaining_seconds())에서 시작하는 태스크(task-1 등)의 이름을 변경하고 싶지만, 
    # 이 과정을 create_task로 변경할 경우 비동기 작업이 바로 시작되어 원하는 대기 시간(await asyncio.sleep(...))을 무시하게 됩니다. 
    # 이 문제를 해결하기 위해서는 목표를 달성하는 몇 가지 방법이 있습니다.
# ---------------------------------------------------------------------------- #
# 방법 1: asyncio.sleep을 감싸는 코루틴 사용
# asyncio.sleep 호출을 별도의 코루틴 함수로 감싸고, 이 코루틴에 대해 create_task를 사용한 후 태스크의 이름을 설정할 수 있습니다. 
# 이 때, await을 사용하여 생성한 태스크가 완료될 때까지 기다려서 비동기적인 대기의 효과를 유지합니다.
import asyncio

async def custom_sleep(delay, name):
    task = asyncio.create_task(asyncio.sleep(delay))
    task.set_name(name)
    await task

async def main():
    print("Before sleep")
    await custom_sleep(2, "CustomSleepTask")
    print("After sleep")

asyncio.run(main())

# 이 방법은 asyncio.sleep 호출에 대한 태스크의 이름을 설정할 수 있게 해주지만, 
# 사실상 asyncio.sleep 함수 자체가 이미 비동기 작업을 수행하기 때문에 이런 식으로 감싸는 것은 다소 중복된다는 점을 인지해야 합니다.

# ---------------------------------------------------------------------------- #
# 방법 2: 동기적 대기 후 비동기 태스크 실행
# 특정 조건(예: 시간 경과)을 기다린 후 비동기 태스크를 시작하는 로직이 필요하다면, 타이머 기능을 담당하는 별도의 비동기 함수를 구현하고, 
# 이 함수 내에서 필요한 작업(예: asyncio.sleep 이후 태스크 생성 및 실행)을 수행할 수 있습니다.

import asyncio

async def run_with_delay(delay, func, *args, **kwargs):
    await asyncio.sleep(delay)
    # func는 실행하려는 비동기 함수
    task = asyncio.create_task(func(*args, **kwargs))
    task.set_name("DelayedTask")
    await task

async def some_task():
    print("Task executed")

async def main():
    print("Before delayed task")
    await run_with_delay(2, some_task)
    print("After delayed task")

asyncio.run(main())

# 이 방법은 대기 후 태스크를 실행하는 로직을 명확히 분리해주며, 태스크의 이름을 직접 설정할 수 있는 장점이 있습니다.

# 방법 선택
# 위 방법들은 각각 다른 시나리오에 적합할 수 있으며, 구현하고자 하는 기능과 코드의 구조에 따라 적절한 방법을 선택해야 합니다. 
# 첫 번째 방법은 비동기 sleep 호출을 명시적으로 태스크로 관리하고 싶을 때 유용하고, 두 번째 방법은 더 복잡한 로직을 대기 시간 이후에 실행하고자 할 때 적합합니다.