from configparser import ConfigParser
import sys, asyncio
import psycopg


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
        
    # -------------------------------- connect ------------------------------- #
    def _get_connect_str(self):
        host=self.config.get('connect','host')
        port=self.config.get('connect','port')
        user=self.config.get('connect','user')
        password=self.config.get('connect','password')
        dbname=self.config.get('connect','database')
        conn_str = f"dbname={dbname} user={user} password={password} host={host} port={port}"
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
        return psycopg.connect(self.conn_str)

    def xconnect(self):
        """>>> return psycopg.AsyncConnection.connect()"""
        return psycopg.AsyncConnection.connect(self.conn_str)

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
