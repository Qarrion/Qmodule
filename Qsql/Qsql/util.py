from Qsql.connect import Connect








class Util(Connect):

    def __init__(self):
        super().__init__()

    def _fetch_all(self, query:str, vars=None):
        """return rows, desc"""
        with self.connect_pgsql() as conn:
            curs=conn.cursor()
            curs.execute(query, vars)
            rows = curs.fetchall()
            desc = curs.description
        return rows, desc

    def varchar_len(self, text):
        query = "SELECT LENGTH(%s) AS Length"
        with self.connect_pgsql() as conn:
            curs = conn.cursor()
            curs.execute(query, (text,))
            row = curs.fetchone()
        return row[0] if row else None
    
    def table_like(self, text):
        query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
        with self.connect_pgsql() as conn:
            curs = conn.cursor()
            curs.execute(query)
            tables = curs.fetchall()
            tables = [t[0] for t in tables]
            filtered = [table for table in tables if text.upper() in table.upper()]
        return filtered

    def table_cols(self, table):
        _, desc = self._fetch_all(f'select * from {table} LIMIT 1;')
        cols = [v[0] for v in desc]
        oids = [v[1] for v in desc] # oid
        dict_col_oid =  dict(zip(cols, oids))
        rows, _ = self._fetch_all("SELECT oid, typname FROM pg_type WHERE oid IN %s",(tuple(oids),))
        dict_oid_pgtype = dict(rows)

        return {col: {'oid': oid, 'pg_type': dict_oid_pgtype[oid]} for col, oid in dict_col_oid.items()}

    def table_pkey(self, table):
        query = f"""
            SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table}'
                AND CONSTRAINT_NAME LIKE 'PK_%%'"""
        rows,_ = self._fetch_all(query)
        return [v[0] for v in rows]

if __name__=="__main__":
    util = Util()
    print("="*20)
    print(util.varchar_len('test string'))
    print("="*20)
    print(util.table_like('raw'))
    print("="*20)
    print(util.table_cols('raw_trade_data'))
    print("="*20)
    print(util.table_pkey('raw_trade_data'))
    print("="*20)
    print(util.get_hypertable_columns('raw_trade_data'))