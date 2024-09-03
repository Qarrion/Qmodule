import asyncio
from Qlogger import Logger

class Limiter:

    def __init__(self) -> None:
        self.q = asyncio.Queue(3)
        self.logger = Logger('test', clsname='A')

    async def func(self,x):
        future = asyncio.Future()
        await self.q.put((future,x))
        result = await future
        return result
    
    async def work(self):
        while True:
            future, item = await self.q.get()
            self.logger.info.msg('get', item)
            future.set_result(item*10)




if __name__ == "__main__":

    limiter = Limiter()

    async def task():
        resp = await limiter.func(1)
        resp = await limiter.func(2)
        resp = await limiter.func(3)
        resp = await limiter.func(4)

    async def main():
        w = asyncio.create_task(limiter.work())

        await task()

        await w


    asyncio.run(main())