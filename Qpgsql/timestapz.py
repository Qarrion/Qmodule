

from psycopg.rows import namedtuple_row
from Qpgsql import Pgsql
from pprint import pprint



# ---------------------------------------------------------------------------- #
pgsql = Pgsql()
q = """SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s"""

with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        curs.execute(q, ('public', 'candle_m1'))
        rslt = curs.fetchall()
pprint(rslt)

# ---------------------------------------------------------------------------- #
from datetime import datetime


print("naive-----------------------")
dtime_nav = datetime(2024,1,10,10,10)
print(f"{dtime_nav = :}")
stamp_nav = dtime_nav.timestamp()
print(f"{stamp_nav = :}")
print("------------------------naive")
# ---------------------------------------------------------------------------- #


import pytz
kst = pytz.timezone('Asia/Seoul')
utc = pytz.timezone('UTC')
print()
print("astimezone------------------")
print(dtime_nav, dtime_nav.timestamp())
print(dtime_nav.astimezone(kst),dtime_nav.astimezone(kst).timestamp())
print(dtime_nav.astimezone(utc),dtime_nav.astimezone(utc).timestamp())
print("------------------astimezone")



print()
print()
print("localize--------------------")
# 현재 KST 시간 생성
dtime_kst = kst.localize(dtime_nav)
print(f"{dtime_kst = :}")

stamp_kst = dtime_kst.timestamp()
print(f"{stamp_kst = :}")

print()
# 현재 KST 시간 생성
dtime_utc = utc.localize(dtime_nav)
print(f"{dtime_utc = :}")

stamp_utc = dtime_utc.timestamp()
print(f"{stamp_utc = :}")
print("--------------------localize")



# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #



with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        query = """
                select time 
                from candle_m1
                where market='KRW-BTC'
                and time = '2024-01-10 10:10:00 +09:00'
                """
        curs.execute(query)
        rslt = curs.fetchall()

print()
print("select time")
print(rslt[0].time)
print(rslt[0].time.timestamp())



with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        query = """
                select time AT TIME ZONE 'Asia/Seoul' as time 
                from candle_m1
                where market='KRW-BTC'
                and time = '2024-01-10 10:10:00 +09:00'
                """
        curs.execute(query)
        rslt = curs.fetchall()

print()
print("select time AT TIME ZONE 'Asia/Seoul' as time ")
print(rslt[0].time)
print(rslt[0].time.timestamp())


with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        query = """
                select EXTRACT(EPOCH FROM time) AS time
                from candle_m1
                where market='KRW-BTC'
                and time = '2024-01-10 10:10:00 +09:00'
                """
        curs.execute(query)
        rslt = curs.fetchall()

print()
print("select EXTRACT(EPOCH FROM time) AS time")
print(datetime.fromtimestamp(float(rslt[0].time)))
print(rslt[0].time)


with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        query = """
                select EXTRACT(EPOCH FROM time) :: double precision AS time
                from candle_m1
                where market='KRW-BTC'
                and time = '2024-01-10 10:10:00 +09:00'
                """
        curs.execute(query)
        rslt = curs.fetchall()

print()
print("select EXTRACT(EPOCH FROM time) :: double precision AS time")
print(datetime.fromtimestamp(float(rslt[0].time)))
print(rslt[0].time)



with pgsql.connect() as conn:
    with conn.cursor(row_factory=namedtuple_row) as curs:
        query = """
                select EXTRACT(EPOCH FROM time AT TIME ZONE 'Asia/Seoul') AS time
                from candle_m1
                where market='KRW-BTC'
                and time = '2024-01-10 10:10:00 +09:00'
                """
        curs.execute(query)
        rslt = curs.fetchall()

print()
print("select EXTRACT(EPOCH FROM time AT TIME ZONE 'Asia/Seoul') AS time")
print(datetime.fromtimestamp(float(rslt[0].time)))
print(rslt[0].time)