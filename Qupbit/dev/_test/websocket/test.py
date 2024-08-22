import websockets
import asyncio
import uuid
import json

# https://docs.upbit.com/reference/websocket-request-format
# https://jsp-dev.tistory.com/341
url = 'wss://api.upbit.com/websocket/v1'
request_format = [
    {'ticket':str(uuid.uuid4)[:6]},
    {
        'type' : 'ticker',
        'codes': ['KRW-BTC', 'KRW-ETH'],
        'isOnlyRealtime': True
    }

]
send_data = json.dumps(request_format)
async def connect():
    async with websockets.connect(url) as ws:
        await ws.send(send_data)
        while True:
            try :
                data = await ws.recv()
                data = json.loads(data)
                print(data)
            except Exception as e:
                pass


asyncio.run(connect())