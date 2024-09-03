# import asyncio

# async def consumer(condition: asyncio.Condition, name: str):
#     async with condition:
#         print(f"{name} is waiting")
#         await condition.wait()
#         print(f"{name} is notified and consumed the resource")

# async def producer(condition: asyncio.Condition):
#     await asyncio.sleep(1)
#     async with condition:
#         print("Producer is ready to notify")
#         condition.notify_all()

# async def main():
#     condition = asyncio.Condition()

#     consumer1 = asyncio.create_task(consumer(condition, "Consumer 1"))
#     consumer2 = asyncio.create_task(consumer(condition, "Consumer 2"))
#     producer_task = asyncio.create_task(producer(condition))

#     await asyncio.gather(consumer1, consumer2, producer_task)

# asyncio.run(main())

# # ---------------------------------------------------------------------------- #
# import asyncio

# async def task_with_lock(lock, name):
#     print(f"{name} is waiting to acquire the lock")
#     async with lock:
#         print(f"{name} has acquired the lock")
#         await asyncio.sleep(1)
#     print(f"{name} has released the lock")

# async def main():
#     lock = asyncio.Lock()
#     await asyncio.gather(
#         task_with_lock(lock, "Task 1"),
#         task_with_lock(lock, "Task 2"),
#     )

# asyncio.run(main())
# # ---------------------------------------------------------------------------- #
# import asyncio

# #! 여러 코루틴이 condition lcok으로 들어올수 있다 
# #! 단 처음 condition lock에서 wait를 만낫을 경우만!

# async def consumer(condition, name, sec=0):
#     print('to condition')
#     async with condition:
#         print('in condition')
#         await asyncio.sleep(sec)
#         print(f"{name} is waiting for the condition")
#         await condition.wait()
#         print(f"{name} received the notification")

# async def producer(condition):
#     await asyncio.sleep(1)
#     async with condition:
#         print("Producer is notifying the consumers")
#         condition.notify_all()

# async def main():
#     condition = asyncio.Condition()
#     await asyncio.gather(
#         consumer(condition, "Consumer 1", sec=5),
#         consumer(condition, "Consumer 2"),
#         producer(condition),
#     )

# asyncio.run(main())

# ---------------------------------------------------------------------------- #
import asyncio

#! 여러 코루틴이 condition lcok으로 들어올수 있다 
#! 단 처음 condition lock에서 wait를 만낫을 경우만!

# Task Consumer 1 Task: to condition
# Task Consumer 1 Task: in condition
# Task Consumer 2 Task: to condition
# Task Consumer 1 Task: Consumer 1 is waiting for the condition
# Task Consumer 2 Task: in condition
# Task Consumer 2 Task: Consumer 2 is waiting for the condition
# Task Producer Task: Producer is notifying the consumers
# Task Consumer 1 Task: Consumer 1 received the notification
# Task Consumer 2 Task: Consumer 2 received the notification
async def consumer(condition, name, sec=0):
    task = asyncio.current_task()
    print(f"Task {task.get_name()}: to condition")
    async with condition:
        print(f"Task {task.get_name()}: in condition")
        await asyncio.sleep(sec)
        print(f"Task {task.get_name()}: {name} is waiting for the condition")
        await condition.wait()
        print(f"Task {task.get_name()}: {name} received the notification")

async def producer(condition):
    task = asyncio.current_task()
    await asyncio.sleep(1)
    async with condition:
        print(f"Task {task.get_name()}: Producer is notifying all the consumers")
        condition.notify_all()

async def main():
    condition = asyncio.Condition()

    # 이름을 지정하여 태스크를 생성
    consumer1 = asyncio.create_task(consumer(condition, "Consumer 1"))
    consumer1.set_name("Consumer 1 Task")
    
    consumer2 = asyncio.create_task(consumer(condition, "Consumer 2"))
    consumer2.set_name("Consumer 2 Task")
    
    producer_task = asyncio.create_task(producer(condition))
    producer_task.set_name("Producer Task")

    await asyncio.gather(consumer1, consumer2, producer_task)

asyncio.run(main())