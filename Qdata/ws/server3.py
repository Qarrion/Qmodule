# import asyncio
# import websockets
# import time

# async def echo(websocket, path):
#     start_time = time.time()
#     print(f"Client connected: {websocket.remote_address}")
#     try:
#         while True:
#             elapsed_time = time.time() - start_time
#             await websocket.send(f"Connected for {int(elapsed_time)} seconds")
#             await asyncio.sleep(1)
#     except websockets.ConnectionClosed:
#         print(f"Client disconnected: {websocket.remote_address}")

# start_server = websockets.serve(echo, "localhost", 8765)

# asyncio.get_event_loop().run_until_complete(start_server)
# print("WebSocket server started on ws://localhost:8765")
# asyncio.get_event_loop().run_forever()





import asyncio
import websockets
import time

async def echo(websocket, path):
    start_time = time.time()
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            elapsed_time = time.time() - start_time
            await websocket.send(f"Connected for {int(elapsed_time)} seconds")
            await asyncio.sleep(1)
            if elapsed_time > 10:
                print(f"Closing connection to {websocket.remote_address}")
                await websocket.close()
                break
            
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("[server] WebSocket server started at ws://localhost:8765")
        await asyncio.Future()  # 서버가 종료되지 않도록 대기


asyncio.run(main())