import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', type=int, default=0)
args = parser.parse_args()


import time
import asyncio
import websockets

if args.server == 0:
    # ------------------------------------------------------------------------ #
    async def handler(websocket, path):
        print(f"[sv] {"connected":>10} : {'client'}")
        async for message in websocket:
            print(f"[sv] {"recived":>10} : {message}")
            await websocket.send(f"Echo: {message}")
            print(f"[sv] send(echo) : {message}")
            print("-------------------------------------------------")
        print(f"[sv] {"closed":>10} : {'client'}")

if args.server == 1:
    async def handler(websocket, path):
        start_time = time.time()
        print(f"[sv] {"connected":>10} : {'client'}")
        try:
            while True:
                elapsed_time = time.time() - start_time

                await websocket.send(f"Connected for {int(elapsed_time)} seconds")
                print(f"[sv] {"send":>10} : {'msg'}")
                await asyncio.sleep(1)
                # 10초 후 클라이언트 연결 종료
                if elapsed_time > 10:
                    # print(f"Closing connection to {websocket.remote_address}")
                    print(f"[sv] {"close":>10} : {'connection'}")
                    await websocket.close()
                    break
        except websockets.ConnectionClosed:
            print(f"[sv] {"disconnected":>10} : {'client'}")






async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print(f"[sv] {"started":>10} : {'server'}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())