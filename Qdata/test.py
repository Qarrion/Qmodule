


# https://websockets.readthedocs.io/en/stable/howto/autoreload.html
# https://technfin.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%97%85%EB%B9%84%ED%8A%B8-%EC%9B%B9%EC%86%8C%EC%BC%93-%EC%A0%91%EC%86%8D%EB%B0%A9%EB%B2%95-%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8-%EC%9E%90%EB%8F%99%EB%A7%A4%EB%A7%A4-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8




import asyncio
from typing import Literal
import websockets
import json
import uuid 




# def get_request_formet(ticket=None, type:Literal['ticker','trade','order']='ticker', codes=[], isOnlySnapshot=None, ):
#     request_format = [
#         {"ticket": ticket},
#         {
#             "type": type,
#             "codes": codes,
#             "isOnlyRealtime": True
#         },
#         {"format": format}
#     ]

async def client():
    uri = "wss://api.upbit.com/websocket/v1"
    async for websocket in websockets.connect(uri, ping_interval=60):
        print(f"[cl] {"connected":>10} : {'server'}")

        ticket = str(uuid.uuid4())[:8]
        types = 'ticker'
        codes=['KRW-BTC']
        format='SIMPLE'

        request_format = [
            {"ticket": ticket},
            {
                "type": types,
                "codes": codes,
                # "isOnlyRealtime": True,
                "isOnlySnapshot": True,
            },
            {"format": format}
        ]

        print(f"[cl] {"send":>10} : {'server'}")
        await websocket.send(json.dumps(request_format))

        while True:
            response = await websocket.recv()
            # print(type(response), response)
            data = json.loads(response)
            # print(type(data), data)
            print(data)

if __name__ == "__main__":
    asyncio.run(client())