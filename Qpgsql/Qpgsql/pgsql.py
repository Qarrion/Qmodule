# -------------------------------- ver 240525 -------------------------------- #
# option 'kst'


from configparser import ConfigParser
import sys, asyncio
from typing import Literal
import psycopg
from psycopg.rows import namedtuple_row

class Pgsql:
    def __init__(self):
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
        """>>> return psycopg.AsyncConnection.connect()"""
        return psycopg.AsyncConnection.connect(self.conn_str)

    # ------------------------------------------------------------------------ #
    #                                   utils                                  #
    # ------------------------------------------------------------------------ #
    def colnames(self, curs:psycopg.Cursor)->list:
        return [d[0] for d in curs.description]
    
    def fetchall(self,conn:psycopg.Connection, query:str, key:Literal['tuple','namedtuple']='tuple'): 
        curs = conn.cursor()
        if key =='namedtuple':
            curs.row_factory = namedtuple_row
        curs.execute(query)
        rows = curs.fetchall()
        return rows
    


if __name__ == "__main__":
    pgsql = Pgsql()
    conn = pgsql.connect()
    # conn_async = pgsql.xconnect()
    # print(conn_async)
    from Qpgsql.utils.print_divider import eprint
    eprint('dir_conn')
    print(dir(conn))
    eprint('dir_conn.autocommit')
    print(conn.autocommit)
    eprint('dir_conn.pipeline')
    print(conn.pipeline)
    eprint('dir_conn.info')
    print(dir(conn.info))
    eprint('dir_conn.pipeline_status')
    print(conn.info.pipeline_status)
    eprint('dir_conn.timezone')
    print(conn.info.timezone)
    eprint('dir_conn.pipeline_status')
    print(conn.info.pipeline_status)
    eprint('dir_conn.dsn')
    print(conn.info.dsn)
    print(pgsql.conn_str)

"""
async with await psycopg.AsyncConnection.connect(
        "dbname=test user=postgres") as aconn:
    async with aconn.cursor() as acur:
        await acur.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))
        await acur.execute("SELECT * FROM test")
        await acur.fetchone()
        # will return (1, 100, "abc'def")
        async for record in acur:
            print(record)
"""