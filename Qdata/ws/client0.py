import asyncio
import websockets

async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = "Hello, WebSocket!"
        while True:
            await asyncio.sleep(1)
            await websocket.send(message)
            
        print(f"Sent message: {message}")
        
        response = await websocket.recv()
        print(f"Received message: {response}")

if __name__ == "__main__":
    asyncio.run(hello())