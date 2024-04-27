import asyncio
import logging
from asyncio import TaskGroup

class PeriodicExecutor:
    def __init__(self, interval_seconds: int = 20):
        self.interval_seconds = interval_seconds
        self.functions = []
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def set_func(self, func):
        self.functions.append(func)

    async def _run_with_timeout(self, func):
        try:
            await asyncio.wait_for(func(), self.interval_seconds)
        except asyncio.TimeoutError:
            self.logger.warning(f"Function {func.__name__} timed out")

    async def start(self):
        while True:
            async with TaskGroup() as tg:
                for func in self.functions:
                    tg.create_task(self._run_with_timeout(func))
            
            await asyncio.sleep(self.interval_seconds)

import datetime
# 예시 사용법
async def example_func1():
    print(f"func1 start {datetime.datetime.now()}")
    await asyncio.sleep(5)
    print(f"func1 finish {datetime.datetime.now()}")
    
async def example_func2():
    print(f"func2 start {datetime.datetime.now()}")
    await asyncio.sleep(10)
    print(f"func2 finish {datetime.datetime.now()}")

async def example_func3():
    print(f"func3 start {datetime.datetime.now()}")
    await asyncio.sleep(30)  # 이 함수는 타임아웃 발생 예정
    print(f"func3 finish {datetime.datetime.now()}")

async def main():
    executor = PeriodicExecutor()
    executor.set_func(example_func1)
    executor.set_func(example_func2)
    executor.set_func(example_func3)

    await executor.start()

asyncio.run(main())