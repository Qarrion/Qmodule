import asyncio
import time

class Limiter:

    def __init__(self):
        self.w = 1
        self._n_worker = 3 
        self.que_i  = asyncio.Queue(self._n_worker)
        self.que_o  = asyncio.Queue(self._n_worker)
        self.condi  = asyncio.Condition()

    async def cut_window(self):
        print('cut_window')
        async with self.condi:
            if self.que_i.full():
                print('full')
                s = self.que_i._queue[0] + self.w - time.time()
                await asyncio.sleep(s)
                await self.que_i.get()
                self.que_i.task_done()     

            while (not self.que_i.empty()) and (self.que_i._queue[0] < time.time() - self.w) :
                await self.que_i.get()
                self.que_i.task_done()     

            return True
    async def put_que(self):
        async with self.condi:
            await self.condi.wait_for(())
            await self.que_i.put(time.time())
        print(asyncio.current_task().get_name(),self.que_i)

    # #! condition은 wait 또는 wait_for일 경우 제어권을 다른 condition에 넘김
    # async def put_que(self):
    #     async with self.condi:
    #         if self.que_i.full():
    #             await self.cut_window()
    #         else:
    #             await self.que_i.put(time.time())
    #     print(asyncio.current_task().get_name(),self.que_i)

if __name__ == "__main__":
    limiter = Limiter()

    async def task0():
        await limiter.put_que()
        await limiter.put_que()
        await limiter.put_que()
        await limiter.put_que()

    async def task1():
        tasks = [
            limiter.put_que(),
            limiter.put_que(),
            limiter.put_que(),
            limiter.put_que(),
        ]
        await asyncio.gather(*tasks)

    async def main():
        await task0()

    asyncio.run(main())