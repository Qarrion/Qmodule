# -------------------------------- ver 240525 -------------------------------- #
# option 'kst'


from configparser import ConfigParser
import sys, asyncio
from typing import Literal
import psycopg
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import namedtuple_row

class Pgsql:
    def __init__(self, msg=False):
        """psycopg wrapper"""
        self.config = ConfigParser()

        if sys.platform =="win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            self.config.read(r'config/db.ini')

        except Exception as e:
            raise UserWarning("""
            project/config/db.ini
            ---------------------
            [connect]
            host = xxx.xxx.xxx.xxx
            port = xxxx
            user = xxxx
            password = xxxx
            database = xxxx
            ---------------------                  
        """)
        self.conn_str = self._get_connect_str()
        self.namedtuple_row=namedtuple_row

    def _dev_help(self):
        print("https://www.psycopg.org/psycopg3/docs/advanced/async.html")
        
    # ------------------------------------------------------------------------ #
    #                                  connect                                 #
    # ------------------------------------------------------------------------ #
    def _get_connect_str(self):
        host=self.config.get('connect','host')
        port=self.config.get('connect','port')
        user=self.config.get('connect','user')
        password=self.config.get('connect','password')
        dbname=self.config.get('connect','database')
        options = "'-c timezone=Asia/Seoul'"
        conn_str = f"dbname={dbname} user={user} password={password} host={host} port={port} options={options}"
        # conn_str = f"dbname={dbname} user={user} password={password} host={host} port={port}"
        return conn_str

    def _connect_kwargs(self):
        cnxn = psycopg.connect(
            host=self.config.get('connect','host'),
            port=self.config.get('connect','port'),
            user=self.config.get('connect','user'),
            password=self.config.get('connect','password'),
            dbname=self.config.get('connect','database')
        )
        return cnxn

    def connect(self):
        """>>> psycopg.connect(self.conn_str)"""
        return psycopg.connect(self.conn_str)

    def xconnect(self):
        """>>> return psycopg.AsyncConnection.connect()
        + insert auto commit after close xconn context
        + await xconn.commit() should be placed in xcurs context"""
        return psycopg.AsyncConnection.connect(self.conn_str)

    def xconnect_pool(self, name='pgsql', num_workers = 5):
        # https://www.psycopg.org/psycopg3/docs/api/pool.html#module-psycopg_pool
        # pool = AsyncConnectionPool(self.conn_str, name=name, num_workers=num_workers)
        pool = AsyncConnectionPool(self.conn_str,open=False, name=name, num_workers=num_workers)
        return pool
    # ------------------------------------------------------------------------ #
    #                                   utils                                  #
    # ------------------------------------------------------------------------ #
    def colnames(self, curs:psycopg.Cursor)->list:
        return [d[0] for d in curs.description]
    
    def _fetchall(self,conn:psycopg.Connection, query:str, key:Literal['tuple','namedtuple']='tuple'): 
        with conn.cursor() as curs:
            if key =='namedtuple':
                curs.row_factory = namedtuple_row
            curs.execute(query)
            rows = curs.fetchall()
        return rows
    
    def fetchall(self,query:str, key:Literal['tuple','namedtuple']='tuple'): 
        with self.connect() as conn:
            return self._fetchall(conn=conn, query=query, key=key)

    async def xfetchall(self,xconn:psycopg.AsyncConnection, query:str, key:Literal['tuple','namedtuple']='tuple'): 
        async with xconn.cursor() as xcurs:
            if key =='namedtuple':
                xcurs.row_factory = namedtuple_row
            await xcurs.execute(query)
            rows = await xcurs.fetchall()
        return rows
    


if __name__ == "__main__":
    import time
    pgsql = Pgsql()
    # conn = pgsql.connect()
    
    # conn_async = pgsql.xconnect()
    # print(conn_async)
    # print('dir_conn')
    # print(dir(conn))
    # print('dir_conn.autocommit')
    # print(conn.autocommit)
    # print('dir_conn.pipeline')
    # print(conn.pipeline)
    # print('dir_conn.info')
    # print(dir(conn.info))
    # print('dir_conn.pipeline_status')
    # print(conn.info.pipeline_status)
    # print('dir_conn.timezone')
    # print(conn.info.timezone)
    # print('dir_conn.pipeline_status')
    # print(conn.info.pipeline_status)
    # print('dir_conn.dsn')
    # print(conn.info.dsn)
    # print(pgsql.conn_str)
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
    # def main1():
    #     with pgsql.connect() as conn:
    #         with conn.cursor() as curs:
    #             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             rows = curs.fetchall()
    #             print(rows[0])
        
    # a = time.time()
    # main1()

    # print('main1',time.time() - a )
    # # ---------------------------------------------------------------------------- #
    # # ---------------------------------------------------------------------------- #
    # async def main2():
    #     async with await pgsql.xconnect() as xconn:
    #         async with xconn.cursor() as xcurs:
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             rows = await xcurs.fetchall()
    #             print(rows[0])
    # a = time.time()
    # asyncio.run(main2())
    # print('main2',time.time() - a )
    # # ---------------------------------------------------------------------------- #
    # # ---------------------------------------------------------------------------- #
    # async def main3():
    #     async with pgsql.xconnect_pool() as xpool:
    #         # xpool.close()
    #         # xpool.closed
    #         async with xpool.connection() as xconn:
    #             async with xconn.cursor() as xcurs:
    #                 await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #                 await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #                 await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #                 rows = await xcurs.fetchall()
    #                 print(rows[0])
    # a = time.time()
    # asyncio.run(main3())
    # print('main3',time.time() - a )

    # ---------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------- #

    async def main4():
        xpool = pgsql.xconnect_pool()
        await xpool.open()

        # async with pgsql.xconnect_pool() as xpool:
            # xpool.close()
            # xpool.closed
        async with xpool.connection() as xconn:
            async with xconn.cursor() as xcurs:
                await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
                await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
                await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")

                # print(rows)
    a = time.time()
    asyncio.run(main4())
    print(time.time() - a )


# ---------------------------------------------------------------------------- #
    # main1()
    # asyncio.run(main2())




















    # ------------------------------------------------------------------------ #
    # async def create():
    #     q = """
    #     CREATE TABLE tbl_test (
    #         id SERIAL PRIMARY KEY,
    #         name VARCHAR(100) NOT NULL,
    #         age INTEGER NOT NULL
    #     )"""
    #     async with await pgsql.xconnect() as aconn:
    #         async with aconn.cursor() as acur:
    #             await acur.execute(q)
    # ------------------------------------------------------------------------ #
    # async def insert():
    #     async with await pgsql.xconnect() as aconn:
    #         async with aconn.cursor() as acurs:
    #             # tbl_test 테이블에 데이터를 삽입하는 SQL 쿼리
    #             insert_query = """
    #             INSERT INTO tbl_test (name, age) VALUES (%s, %s)
    #             """
                
    #             # 삽입할 데이터
    #             data_to_insert = [
    #                 ("Alice", 30),
    #                 ("Bob", 25),
    #                 # ("Charlie", 35)
    #             ]
                
    #             # 여러 행 삽입
    #             for data in data_to_insert:
    #                 await acurs.execute(insert_query, data)
                
    #             await aconn.commit()
    #         print('acurs out not commit? no ! if then ::aconn.commit()::' )
    #     print('aconn out commit? yes!')
    #             # 변경 사항을 커밋합니다.
    #             # conn.commit()
    #             # print("Data inserted successfully")
    # ------------------------------------------------------------------------ #
#     async def main():
#         # await create()     
#         await insert()     
        
#     asyncio.run(main())
# """
# async with await psycopg.AsyncConnection.connect(
#         "dbname=test user=postgres") as aconn:
#     async with aconn.cursor() as acur:
#         await acur.execute(
#             "INSERT INTO test (num, data) VALUES (%s, %s)",
#             (100, "abc'def"))
#         await acur.execute("SELECT * FROM test")
#         await acur.fetchone()
#         # will return (1, 100, "abc'def")
#         async for record in acur:
#             print(record)
# """

# """
# with pgsql.connect() as conn:
#     with conn.cursor() as curs:
#         curs.row_factory = pgsql.namedtuple_row
#         curs.execute("select * from market_list where market = 'KRW-BTC'")
#         rows = curs.fetchall()
# """
# import timeit
# import time
# ---------------------------------------------------------------------------- #
# def main1():
#     with pgsql.connect() as conn:
#         with conn.cursor() as curs:
#             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
#             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
#             curs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
 
#             # print(rows)
# a = time.time()
# main1()
# print(time.time() - a )
# ---------------------------------------------------------------------------- #




# async def main3():
#     async with pgsql.xconnect_pool() as xpool:
#         # xpool.close()
#         # xpool.closed
#         async with xpool.connection() as xconn:
#             async with xconn.cursor() as xcurs:
#                 # await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
#                 # await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
#                 await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
#                 rows = await xcurs.fetchall()
#             print(rows)
# a = time.time()
# asyncio.run(main3())
# print(time.time() - a )

    # async def main4():
    #     # xpool = pgsql.xconnect_pool()
    #     # xpool.open()
    #     # async with pgsql.xconnect_pool() as xpool:
    #         # xpool.close()
    #         # xpool.closed
    #     async with xpool.connection() as xconn:
    #         async with xconn.cursor() as xcurs:
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    #             await xcurs.execute("select * from candle_m1 where market='KRW-BTC' and time > '2024-01-01 00:00:00' ")
    
    #             # print(rows)
    # a = time.time()
    # asyncio.run(main4())
    # print(time.time() - a )