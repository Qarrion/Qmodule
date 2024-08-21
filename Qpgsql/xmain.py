import asyncio
from Qpgsql import Pgsql






pgsql = Pgsql()

q = "select * from market_list where market = 'KRW-BTC'"
# ------------------------------------- a ------------------------------------ #
# with pgsql.connect() as conn:
#     with conn.cursor() as curs:
#         curs.execute(q)
#         rows = curs.fetchall()

# print(rows)


# # ------------------------------------- x ------------------------------------ #
# q = "select * from market_list where market = 'KRW-BTC'"
# async def xfetch():
#     async with await pgsql.xconnect() as xconn:
#         pass
#         async with xconn.cursor() as xcurs:
#             await xcurs.execute(q)

#             rows = await xcurs.fetchall()

#     print(rows)

# # # # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(xfetch())


# # ------------------------------------- x ------------------------------------ #
q = "select * from market_list where market = %s"
async def xfetch():
    async with await pgsql.xconnect() as xconn:
        pass
        async with xconn.cursor() as xcurs:
            await xcurs.execute(q,('KRW-BTC',))

            rows = await xcurs.fetchall()

    print(rows)

# # # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(xfetch())
