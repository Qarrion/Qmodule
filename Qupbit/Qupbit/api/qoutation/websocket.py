import websockets
import asyncio
import uuid
import json
from typing import Literal


# https://docs.upbit.com/reference/websocket-request-format

class WebsocketClient:
    def __init__(self, type:Literal['ticker','trade','orderbook'], codes: list, queue: asyncio.Queue):
        self.type = type
        self.codes = codes
        self.queue = queue
        # self.run()

    async def connect_socket(self):
        uri = "wss://api.upbit.com/websocket/v1"
        async for websocket in websockets.connect(uri, ping_interval=None, max_queue=10000):
            try:
                data = [
                    {"ticket": str(uuid.uuid4())[:6]}, 
                    {"type": self.type,
                    "codes": self.codes,
                    "isOnlyRealtime": True,
                    # "isOnlySnapshot": True,
                    },
                    {"format":'DEFAULT'}]

                await websocket.send(json.dumps(data))

                while True:
                    recv_data = await websocket.recv()
                    recv_data = recv_data.decode('utf8')
                    await self.queue.put(json.loads(recv_data))

            except asyncio.TimeoutError:
                await asyncio.wait_for(websockets.ping(), timeout=10)
                
            except websockets.exceptions.ConnectionClosed:
                print("try reconnect")
                continue


    async def consumer(self):
        while True:
            data = await self.queue.get()
            print(data)
            self.queue.task_done()


    
if __name__ =="__main__":
    async def main():
        queue = asyncio.Queue()

        # client = WebsocketClient(type='ticker',codes=['KRW-BTC'], queue=queue)
        # client = WebsocketClient(type='trade',codes=['KRW-BTC'], queue=queue)
        # client = WebsocketClient(type='orderbook',codes=['KRW-BTC'], queue=queue)
        client = WebsocketClient(type='trade',codes=['KRW-FLOW'], queue=queue)
        await asyncio.gather(
            client.connect_socket(), 
            client.consumer())
    
    asyncio.run(main())



# {'type': 'trade', 
#  'code': 'KRW-FLOW', 
#  'timestamp': 1704893597932, 
#  'trade_date': '2024-01-10', 
#  'trade_time': '13:33:17', 
#  'trade_timestamp': 1704893597908, 
#  'trade_price': 995.0, 
#  'trade_volume': 302.06482125, 
#  'ask_bid': 'ASK', 
#  'prev_closing_price': 1030.0, 
#  'change': 'FALL', 
#  'change_price': 35.0, 
#  'sequential_id': 17048935979080000, 
#  'stream_type': 'REALTIME'}
    
# {'type': 'ticker', 
#  'code': 'KRW-BTC', 
#  'opening_price': 59105000.0, 
#  'high_price': 61118000.0, 
#  'low_price': 57801000.0, 
#  'trade_price': 60242000.0, 
#  'prev_closing_price': 59108000.0, 
#  'acc_trade_price': 409021673646.8982, 
#  'change': 'RISE', 
#  'change_price': 1134000.0, 
#  'signed_change_price': 1134000.0, 
#  'change_rate': 0.0191852203, 
#  'signed_change_rate': 0.0191852203, 
#  'ask_bid': 'BID', 
#  'trade_volume': 0.01579279, 
#  'acc_trade_volume': 6853.7359615, 
#  'trade_date': '20240108', 
#  'trade_time': '150204', 
#  'trade_timestamp': 1704726124883, 
#  'acc_ask_volume': 3256.64642914, 
#  'acc_bid_volume': 3597.08953236, 
#  'highest_52_week_price': 61312000.0, 
#  'highest_52_week_date': '2023-12-06', 
#  'lowest_52_week_price': 21558000.0, 
#  'lowest_52_week_date': '2023-01-10', 
#  'market_state': 'ACTIVE', 
#  'is_trading_suspended': False, 
#  'delisting_date': None, 
#  'market_warning': 'NONE', 
#  'timestamp': 1704726124907, 
#  'acc_trade_price_24h': 475764733916.7084, 
#  'acc_trade_volume_24h': 7980.67211501, 
#  'stream_type': 'REALTIME'}