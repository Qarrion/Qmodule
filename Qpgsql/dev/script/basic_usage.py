from Qpgsql import Pgsql

sql = Pgsql()

# ------------------------------- create table ------------------------------- #
with sql.connect() as conn:
    with conn.cursor() as curs:
        curs.execute("""
            CREATE TABLE test (
                id SERIAL PRIMARY KEY,
                num INTEGER,
                data TEXT,
                timez TIMESTAMPTZ NOT NULL,
                last_updated TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
        conn.commit()


# -------------------------------- insert data ------------------------------- #
from datetime import datetime, timezone 
import time

datetime.now(timezone.utc)
datetime.now()

tnow = time.time()
now = datetime.now()
timestamp = datetime.timestamp(now)
d =1714651979967
d//10

datetime.fromtimestamp(timestamp)

insert_query = """
    INSERT INTO test (num, data, timez)
    VALUES (%s, %s, %s)
    """

# insert_data1 = (10,'test utc', datetime.now(timezone.utc))  # 입력가능
# insert_data2 = (10,'test naive', datetime.now())              # microsecond 까지들어감
# insert_data3 = (10,'test str','2024-03-10 15:02:00+09:00')   # 입력가능

insert_data3 = (10,'test naive','2024-05-02T14:34:00')   # 입력가능
insert_data3 = (10,'test naive','2024-05-02T23:34:00')   # 입력가능
insert_data3 = (10,'test naive','2024-05-02T23:34:00+09:00')   # 입력가능
insert_data3 = (10,'test naive','2024-05-02 23:34:00+09:00')   # 입력가능


from Qpgsql import Pgsql
sql  =  Pgsql()

with sql.connect() as conn:
    with conn.cursor() as curs:
        # curs.execute(insert_query, insert_data1)
        # time.sleep(1)
        # curs.execute(insert_query, insert_data2)
        # time.sleep(1)
        curs.execute(insert_query, insert_data3)
        conn.commit()

# ---------------------------------- select ---------------------------------- #
#! timez 는 datetime(utc)로 출력

with sql.connect() as conn:
    with conn.cursor() as curs:
        curs.execute('SELECT * FROM test')
        rows = curs.fetchall()
print(rows)

from pprint import pprint 
pprint(rows)


rows[0]
rows[1]
rows[2]
rows[3]
rows[4]
# (1, 10, 'test', datetime.datetime(2024, 3, 11, 13, 35, 48, 194681, tzinfo=datetime.timezone.utc), datetime.datetime(2024, 3, 11, 13, 35, 48, 343172, tzinfo=datetime.timezone.utc))
# (2, 10, 'test', datetime.datetime(2024, 3, 11, 13, 37, 3, 55371, tzinfo=datetime.timezone.utc), datetime.datetime(2024, 3, 11, 13, 37, 3, 201915, tzinfo=datetime.timezone.utc))
# (3, 10, 'test', datetime.datetime(2024, 3, 11, 13, 37, 41, 83189, tzinfo=datetime.timezone.utc), datetime.datetime(2024, 3, 11, 13, 37, 41, 229004, tzinfo=datetime.timezone.utc))
# (4, 10, 'test', datetime.datetime(2024, 3, 11, 22, 39, 4, 151223, tzinfo=datetime.timezone.utc), datetime.datetime(2024, 3, 11, 13, 39, 4, 297362, tzinfo=datetime.timezone.utc))
# (5, 10, 'test', datetime.datetime(2024, 3, 10, 6, 2, tzinfo=datetime.timezone.utc), datetime.datetime(2024, 3, 11, 13, 40, 11, 480841, tzinfo=datetime.timezone.utc))

# ---------------------------- select as time zone --------------------------- #
#! [timez AT TIME ZONE 'Asia/Seoul' as timez_kst] 의 경우 datetime(naive)형태로 출력 
select_query = """
select id, num, data,
timez AT TIME ZONE 'Asia/Seoul' as timez_kst,
last_updated
from test;"""
with connection.open() as conn:
    with conn.cursor() as curs:
        curs.execute(select_query)
        rows = curs.fetchall()
rows[0]
rows[1]
rows[2]
rows[3]
rows[4]

# (1, 10, 'test', datetime.datetime(2024, 3, 11, 22, 35, 48, 194681), datetime.datetime(2024, 3, 11, 13, 35, 48, 343172, tzinfo=datetime.timezone.utc))
# (2, 10, 'test', datetime.datetime(2024, 3, 11, 22, 37, 3, 55371), datetime.datetime(2024, 3, 11, 13, 37, 3, 201915, tzinfo=datetime.timezone.utc))
# (3, 10, 'test', datetime.datetime(2024, 3, 11, 22, 37, 41, 83189), datetime.datetime(2024, 3, 11, 13, 37, 41, 229004, tzinfo=datetime.timezone.utc))
# (4, 10, 'test', datetime.datetime(2024, 3, 12, 7, 39, 4, 151223), datetime.datetime(2024, 3, 11, 13, 39, 4, 297362, tzinfo=datetime.timezone.utc))
# (5, 10, 'test', datetime.datetime(2024, 3, 10, 15, 2), datetime.datetime(2024, 3, 11, 13, 40, 11, 480841, tzinfo=datetime.timezone.utc))
rows[4][3].tzinfo
rows[4][4].tzinfo