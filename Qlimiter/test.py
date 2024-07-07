import httpx
import asyncio as x


async def test():

    conn = await httpx.AsyncClient()

x.run(test())
    