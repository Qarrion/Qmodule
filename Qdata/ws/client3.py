# import asyncio
# import websockets

# async def listen():
#     uri = "ws://localhost:8765"
#     async with websockets.connect(uri) as websocket:
#         try:
#             while True:
#                 message = await websocket.recv()
#                 print(f"Received: {message}")
#         except websockets.ConnectionClosed:
#             print("Connection closed by server")

# asyncio.get_event_loop().run_until_complete(listen())



# # ---------------------------------- 재연결 구현 ---------------------------------- #
# import asyncio
# import websockets

# async def listen():
#     uri = "ws://localhost:8765"
#     while True:
#         try:
#             async with websockets.connect(uri) as websocket:
#                 print("Connected to the server")
#                 while True:
#                     message = await websocket.recv()
#                     print(f"Received: {message}")
#         except websockets.ConnectionClosed:
#             print("Connection closed by server. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)

# asyncio.get_event_loop().run_until_complete(listen())

# ---------------------------------------------------------------------------- #
import asyncio
import websockets

async def listen(uri):
    async for websocket in websockets.connect(uri):
        try:
            print("Connected to the server")
            async for message in websocket:
                print(f"Received: {message}")
                
        except websockets.ConnectionClosed:
            print("Connection closed by server. Reconnecting...")

asyncio.run(listen("ws://localhost:8765"))