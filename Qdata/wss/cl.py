import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--client', type=int, default=0)
args = parser.parse_args()



import asyncio
import websockets

# ---------------------------------------------------------------------------- #
if args.client ==0:
    
    async def client():
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            print(f"[cl] {"connected":>10} : {'server'}")

            print(f"[cl] {"send":>10} : {'server'}")
            await websocket.send("Hello, world!")
            response = await websocket.recv()
            print(f"[cl] {"recv":>10} : {response}")

# ---------------------------------------------------------------------------- #
if args.client ==1:
    async def client():
        uri = "ws://localhost:8765"
        async for websocket in websockets.connect(uri, ping_interval=60):
            try:
                print(f"[cl] {"connected":>10} : {'server'}")
                async for message in websocket:
                    print(f"[cl] {"recv":>10} : {message}")
            except websockets.ConnectionClosed:
                print("Connection closed by server. Reconnecting...")
            except ConnectionRefusedError:
                print("Connection refused by server. Reconnecting in 5 seconds...")
            finally:
                print("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                


if __name__ == "__main__":
    asyncio.run(client())