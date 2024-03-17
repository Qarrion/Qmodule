from Qlimiter import AsyncLimiter
from Qlogger import Logger


if __name__ == "__main__":
    import asyncio

    logger = Logger('test', 'head', debug=False)
    logger._dev_stream_handler_level('INFO')
    limiter = AsyncLimiter(3, 1, 'outflow', logger=logger)
    async def myfunc1(x):
        await asyncio.sleep(x)

    async def myfunc2(x):
        raise Exception("raise Error")

    async def main():
        limiter.register(myfunc1)
        limiter.register(myfunc2)

        await limiter.enqueue('myfunc1',(1,))
        await limiter.enqueue('myfunc2',(2,))
        await limiter.taskgroup()

    asyncio.run(main())
