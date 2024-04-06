from configparser import ConfigParser
import psycopg

class Pgsql:
    def __init__(self):
        self.config = ConfigParser()

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
    
    def connect_async(self):
        return psycopg.AsyncConnection.connect(self.conn_str)

if __name__ == "__main__":
    pgsql = Pgsql()
    conn = pgsql.connect()
    conn_async = pgsql.connect_async()
    print(conn_async)
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
