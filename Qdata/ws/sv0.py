# import asyncio
# import websockets


# async def handler(websocket):
#     print('[sv] client connected')

#     while True:
#         message = await websocket.recv()
#         print(f'[sv] client message : {message}')

# async def main():
#     async with websockets.serve(handler, "localhost", 8765):
#         print("[sv] started")
#         await asyncio.Future()  # run forever


# if __name__ == "__main__":
#     asyncio.run(main())



import asyncio
import websockets


async def handler(websocket):
    print('[sv] client connected')

    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            print(f'[sv] client closed')
        print(f'[sv] client message : {message}')

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("[sv] started")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())