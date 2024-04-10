from Qpgsql import Pgsql

sql = Pgsql()

# ---------------------------------------------------------------------------- #
query = "select * from market_list where market <> ALL(%s)"


data = ['KRW-BTC', 'KRW-ETH']
# data = ['KRW-ETH']
# # print(tuple(data))


with sql.connect() as conn:
    with conn.cursor() as curs:
        curs.execute(query, [data])
        rows = curs.fetchall()


print(rows)
print(len(rows))
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