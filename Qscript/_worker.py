import asyncio

async def worker(worker_id, pause_event, condition):
    while True:
        # pause_event가 set될 때까지 대기
        await pause_event.wait()

        async with condition:
            # 워커가 대기 상태에 진입했음을 알림
            print(f"Worker {worker_id} ({asyncio.current_task().get_name()}) is now waiting...")
            condition.notify_all()  # 다른 코루틴들에게 상태 변화를 알림

        # 실제 작업 수행
        print(f"Worker {worker_id} ({asyncio.current_task().get_name()}) is working...")
        await asyncio.sleep(1)  # 작업을 수행하는 데 걸리는 시간 (1초 대기)

async def pause_workers(pause_event, condition):
    # 모든 워커를 대기 상태로 만들기 위해 pause_event를 clear
    pause_event.clear()
    print("Pausing all workers...")

    # 모든 워커가 대기 상태에 도달했는지 확인
    async with condition:
        await condition.wait_for(lambda: not pause_event.is_set())
        print("All workers are paused.")

    # 일정 시간 대기 후 다시 시작
    await asyncio.sleep(5)

    # 다시 시작
    pause_event.set()
    print("All workers are resumed.")

async def main():
    # pause_event 초기화, 초기 상태는 set (워커들이 바로 작동 가능)
    pause_event = asyncio.Event()
    pause_event.set()

    # Condition 객체 생성
    condition = asyncio.Condition()

    # 3개의 워커를 생성하고 시작
    workers = [
        asyncio.create_task(worker(i, pause_event, condition), name=f"Task-{i+1}")
        for i in range(3)
    ]

    # 작업 도중 임의의 시간에 워커들을 일시 중지 및 재개
    await asyncio.sleep(5)  # 5초 후 모든 워커 일시 중지
    await pause_workers(pause_event, condition)

    # 워커들을 다시 실행 (무한 실행)
    await asyncio.gather(*workers)

# asyncio.run을 사용하여 이벤트 루프 실행
if __name__ == "__main__":
    asyncio.run(main())
