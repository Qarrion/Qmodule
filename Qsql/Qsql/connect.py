from sqlalchemy import create_engine
from configparser import ConfigParser
import psycopg2







class Connect:
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
    def connect_pgsql(self):
        cnxn = psycopg2.connect(
            host=self.config.get('connect','host'),
            port=self.config.get('connect','port'),
            user=self.config.get('connect','user'),
            password=self.config.get('connect','password'),
            database=self.config.get('connect','database')
        )
        return cnxn
    
    def connect_engine(self):
        conn_str=\
            f"postgresql://{self.config.get('connect','user')}"\
            f"{self.config.get('connect','password')}@{self.config.get('connect','host')}"\
            f"{self.config.get('connect','port')}@{self.config.get('connect','database')}"
        return create_engine(conn_str)