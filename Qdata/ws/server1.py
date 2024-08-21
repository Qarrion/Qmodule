import asyncio
import websockets
from websockets.exceptions import ConnectionClosed

async def echo(websocket, path):
    # 클라이언트가 연결되었을 때 출력
    client_address = websocket.remote_address
    print(f"[server] Client connected: {client_address}")

    try:
        async for message in websocket:
            print(f"[server] recv message from {client_address}: {message}")
            print(f"[server] send message from {client_address}: {message}")
            await websocket.send(f"Echo: {message}")
    except ConnectionClosed:
        # 클라이언트가 연결이 종료되었을 때 출력
        print(f"Client disconnected: {client_address}")
    # finally:
    #     # 클라이언트가 연결이 종료되었을 때 출력 (예외가 발생하지 않는 경우도 처리)
    #     if websocket.closed:
    #         print(f"Client disconnected: {client_address}")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("[server] WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # 서버가 종료되지 않도록 대기

if __name__ == "__main__":
    asyncio.run(main())
