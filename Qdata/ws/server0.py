import asyncio
import websockets

async def echo(websocket, path):
    print('[sv] client connected')
    print(websocket.remote_address)
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("[sv] started")
        await asyncio.Future()  # 서버가 종료되지 않도록 대기

if __name__ == "__main__":
    asyncio.run(main())