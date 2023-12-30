import asyncio
import websockets
import uuid
import json 

async def pingpong():

    request_format = [
        {'ticket':str(uuid.uuid4)[:6]},
        {
            'type' : 'ticker',
            'codes': ['KRW-BTC', 'KRW-ETH'],
            'isOnlyRealtime': True
        }
    ]
    send_data = json.dumps(request_format)


    # url = 'wss://api.upbit.com/websocket/v1'
    url = "ws://localhost:8765"
    async with websockets.connect(url, ping_interval=None) as ws:
        await ws.send(send_data)

        while True:
            # data = await ws.recv()
            # data = json.loads(data)
            # print(data)
            # print("connected")
            pong = await ws.ping()
            print("send ping")
            await asyncio.wait_for(pong, timeout=10)
            print("recv pong")

asyncio.run(pingpong())