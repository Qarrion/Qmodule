import asyncio
import psycopg
from psycopg import AsyncConnectionPool

class DbClient:
    def __init__(self):
        self.dbpool: AsyncConnectionPool = None

    async def start(self):
        self.dbpool = await AsyncConnectionPool.connect(
            dsn="dbname=test user=postgres password=secret host=localhost port=5432",
            min_size=1,
            max_size=10,
        )
        print('Connection pool started')

    async def close_client(self):
        if self.dbpool is not None:
            await self.dbpool.close()
            self.dbpool = None
            print('Connection pool closed')

    async def fetch_data(self, query, batch_size=1000):
        async with self.dbpool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                while True:
                    rows = await cur.fetchmany(batch_size)
                    if not rows:
                        break
                    yield rows

async def process_data_in_batches(db_client, query):
    async for batch in db_client.fetch_data(query):
        for row in batch:
            # 데이터 처리 로직을 여기에 추가합니다.
            print(row)

async def main():
    db_client = DbClient()
    await db_client.start()
    
    query = "SELECT * FROM large_table"
    await process_data_in_batches(db_client, query)
    
    await db_client.close_client()

asyncio.run(main())