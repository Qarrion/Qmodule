# import asyncio
# import websockets

# async def main():
#     uri = "ws://localhost:8765"
#     async with websockets.connect(uri) as websocket:
#         print("Connected to the server")
#         await websocket.send("Hello, Server!")
#         print("Message sent to the server")

#         # 명시적으로 종료
#         await websocket.close()
# if __name__ == "__main__":
#     asyncio.run(main())



import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.get_event_loop().run_until_complete(listen())