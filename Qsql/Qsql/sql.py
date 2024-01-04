from Qsql.connect import Connect
from Qsql.util import Util


import pandas as pd





class Sql(Connect):

    def __init__(self):
        super().__init__()
        self.util = Util()

    # --------------------------------- fetch -------------------------------- #
    def fetch_all(self, query:str, vars=None):
        """return rows, desc"""
        with self.connect_pgsql() as conn:
            curs=conn.cursor()
            curs.execute(query, vars)
            rows = curs.fetchall()
            desc = curs.description
        return rows, desc
    
    def fetch_dfr(self, query:str):
        rows, desc = self.fetch_all(query)
        colnames = [d[0] for d in desc]
        if len(rows) == 0:
            dfr = pd.DataFrame(columns=colnames)
        else:    
            dfr = pd.DataFrame.from_records(rows)
            dfr.columns = colnames
        return dfr
    
    # -------------------------------- pandas -------------------------------- #
    def pd_read_sql(self, query:str):
        return pd.read_sql(query, self.connect_pgsql())
    
    def cast_series(self, series:pd.Series, coltype:type):
        mask = series.notna()
        series = series.where(mask,None).astype(coltype)
        if coltype == str:
            series = series.where(mask, None)
        return series
    
    def sync_table(self, dfr:pd.DataFrame, table:str):
        print("pass !")
        cols = self.util.table_cols(table)
        for col in cols:
            pass

    # -------------------------------- execute ------------------------------- #
    def execute_dfr(self, query:str, dfr:pd.DataFrame, batch_size=1000):
        with self.connect_pgsql() as conn:
            conn.autocommit=False
            curs = conn.cursor()
            for idx, row in dfr.iterrows():
                rslt = curs.execute(query, *row)
                if(idx)%batch_size==0:
                    curs.commit()
                    print(f"\r{idx}/{dfr.shape[0]}", end="")
            curs.commit()
            print(f"\r{idx}/{dfr.shape[0]}")

if __name__ == "main":
    sql = Sql()