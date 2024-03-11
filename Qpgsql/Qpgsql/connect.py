from configparser import ConfigParser
import psycopg

class Connection:
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
    # -------------------------------- connect ------------------------------- #
    def open(self):
        cnxn = psycopg.connect(
            host=self.config.get('connect','host'),
            port=self.config.get('connect','port'),
            user=self.config.get('connect','user'),
            password=self.config.get('connect','password'),
            dbname=self.config.get('connect','database')
        )
        return cnxn

if __name__ == "__main__":
    config = ConfigParser()
    config.read(r'config/db.ini')
    connection = Connection()
    conn = connection.open()
    print(dir(conn))
    print(dir(conn.info))
    print(conn.autocommit)
    print(conn.info.status)
    print(conn.info.timezone)
    print(conn.info.password)

    

    