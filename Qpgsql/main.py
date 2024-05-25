from Qpgsql import Pgsql

sql = Pgsql()

# ---------------------------------------------------------------------------- #
# query = "select * from market_list where market <> ALL(%s)"

# data = ['KRW-BTC', 'KRW-ETH']
# # data = ['KRW-ETH']
# # # print(tuple(data))

# with sql.connect() as conn:
#     with conn.cursor() as curs:
#         curs.execute(query, [data])
#         rows = curs.fetchall()

# print(rows)
# print(len(rows))
# ---------------------------------------------------------------------------- #

# # query = "select * from market_list where market IN %s"
# query = "SELECT * FROM market_list WHERE market IN %(market)s"

# data = ['KRW-BTC', 'KRW-ETH']
# with sql.connect() as conn:
#     with conn.cursor() as curs:
#         # curs.execute(query, (tuple(data),))
#         curs.execute(query, dict(market = data))
#         rows = curs.fetchall()

# print(rows)

# -------------------------------- row_factory ------------------------------- #
# import sys
# from pympler import asizeof

# query = "select * from market_list"
# query = "select market, korean_name from market_list"
#! from psycopg.rows import namedtuple_row
# with sql.connect() as conn:
#     with conn.cursor() as curs:
#         # curs.row_factory = namedtuple_row
#         curs.execute(query)
#         rows = curs.fetchall()
#         desc = sql.colnames(curs)
# print(asizeof.asizeof(rows))
# print(type(rows[0]))
# print(asizeof.asizeof(rows[0]))


# print(asizeof.asizeof(1,2,3,4,5,6))

# print(rows)
# print(desc)
# print(dir(rows[0]))
# print(rows[0]._fields)

# # ----------------------------------- time ----------------------------------- #
# query = "select * from candle_m1"
# with sql.connect() as conn:
#     with conn.cursor() as curs:
#         curs.execute(query)
#         rows = curs.fetchall()
# ----------------------------------- time ----------------------------------- #
query = "select * from candle_m1"
# query = "show timezone"
with sql.connect() as conn:
    with conn.cursor() as curs:
        curs.execute(query)
        rows = curs.fetchall()

print(rows[0])
# rows