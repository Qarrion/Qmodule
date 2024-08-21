import asyncio
import websockets

async def handler(websocket, path):
    print('[sv] client connected')
    
    async def send_periodically():
        while True:
            await asyncio.sleep(1)  # 5초마다 메시지 전송
            await websocket.send("This is a periodic message")

    send_task = asyncio.create_task(send_periodically())

    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # 메시지에 대한 응답을 보낼 수 있습니다.
            await websocket.send(f"Echo: {message}")
    finally:
        send_task.cancel()


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("[sv] started")
        await asyncio.Future()  # 서버가 종료되지 않도록 대기
        print("[sv] stopped")
            
if __name__ == "__main__":
    asyncio.run(main())
