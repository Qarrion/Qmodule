import asyncio






# async def control(event:asyncio.Event):
    # tasks = [asyncio.create_task(worker(i)) for i in range(3)]







n_waiter = 0
trigger = 0  
async def barrier_wait(condition:asyncio.Condition):
    global trigger
    global n_waiter 
   
    if trigger == 1 :
        async with condition:
            n_waiter+=1
            print(f"n_waiter {n_waiter}")
            await condition.wait()

async def trigger_work(condition:asyncio.Condition):
    global trigger
    global n_waiter

    print('trigger on')
    trigger = 1

    async with condition:
        await condition.wait_for(lambda: n_waiter >= 3) 

        print("do some work")

        trigger = 0

        condition.notify_all()


async def worker(worker_id, condition:asyncio.Condition):
    while True:

        await barrier_wait(condition)
        print(f"Worker {worker_id} is working...")
        await asyncio.sleep(1)  # simulate a blocking task


async def main():
    # 10개의 워커 생성


    condition = asyncio.Condition()


    tasks = [asyncio.create_task(worker(i, condition)) for i in range(3)]

    await asyncio.sleep(5)
    await trigger_work(condition)

    
    # 워커들을 무한히 실행
    await asyncio.gather(*tasks)

    # await task



if __name__ == "__main__":
    asyncio.run(main())




