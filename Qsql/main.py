from Qsql.sql import Sql
from Qsql.util import Util

sql = Sql()

# sql.config.get('connect','user')

# cols = sql._cols('raw_trade_data')
# cols
# oids = [v for k, v in cols.items()]

# # import psycopg2.extensions
# # psycopg2.extensions.string_types[23]

# rows, _ = sql.fetch_all("SELECT oid, typname FROM pg_type WHERE oid IN %s",(tuple(oids),))

# with sql.connect_pgsql() as conn:
#     curs = conn.cursor()
#     curs.execute("SELECT oid, typname FROM pg_type WHERE oid IN %s", (tuple(oids),))
#     rslt = curs.fetchall()
# rslt

# (tuple(oids))

# []

# type(rslt[2][1])
# rslt
# # type_mapping = cursor.fetchall()


# from Qsql.pgsql import PGSql
# sql = PGSql()
# import pandas as pd
# pd.read_sql(sql.connect_engine(), f"select * from raw_trade_data")
# pd.read_sql_query(f"select * from raw_trade_data", sql.connect_engine()).dtypes
# pd.read_sql_table(f"select * from raw_trade_data", sql.connect_engine()).dtypes
# pd.read_sql
# sql.connect_engine().connect()
# # postgresql://username:password@localhost:5432/mydatabase
# # postgresql://username:password@host:port/database


# from sqlalchemy import create_engine
# dd = create_engine(f'postgresql://postgres:2302@192.168.0.23:2302/postgres')
# df = pd.read_sql(sql = f"select * from raw_trade_data",con = dd.connect())
# df.dtypes


# col_types = {'time': 1114, 'symbol': 25, 'price': 701, 'quantity': 701}
# type_mapping = [(25, 'text'), (701, 'float8'), (1114, 'timestamp')]

# # Converting the list of tuples into a dictionary for easier lookup
# type_dict = dict(type_mapping)
# # list(zip([1,2,3],['a','b','c']))

# # Using dictionary comprehension to create the desired structure
# result = {col: {'oid': oid, 'pg_type': type_dict[oid]} for col, oid in col_types.items()}

# result['time']
# # pd.DataFrame(result)
# ---------------------------------------------------------------------------- #
util = Util()


print(util.varchar_len("@#@#12321"))