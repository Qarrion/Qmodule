import asyncio
from datetime import datetime
from random import randint

async def run_job() -> None:
	delay = randint(5, 15)

	print(f'{datetime.now()} sleep for {delay} seconds{asyncio.current_task()}')
	await asyncio.sleep(delay)  # 5~15초 동안 잠자기
	print(f'{datetime.now()} finished ({delay}) sec seconds{asyncio.current_task()}')
	print(dir(asyncio.current_task()))
	print(asyncio.current_task().get_name())
async def main() -> None:
	while True:
		asyncio.create_task(run_job())
		await asyncio.sleep(10)

asyncio.run(main())
