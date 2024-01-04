from Qsql.util import Util
from typing import Union, List, Tuple, Literal, overload, Self





def assert_column(column, cols, atype=Literal["select","condition"]):
    # cols = db columns
    # column = query columns
    if column == "*":
        pass

    elif isinstance(column, str):
        qy_col = column
        if atype == 'select':
            db_col_in_qy_col = [db_col for db_col in cols if db_col.upper() in qy_col.upper()] # max/distinct(cols)
        elif atype == 'condition':
            db_col_in_qy_col = [db_col for db_col in cols if db_col.upper() == qy_col.upper()] # max/distinct(cols)
        assert db_col_in_qy_col , f"column '{column}' invalid"

    elif isinstance(column, list|tuple):
        qy_cols = column
        db_cols_upper = [db_col.upper() for db_col in cols]
        qy_cols_not_in_db_cols = [qy_col for qy_col in qy_cols if qy_col.upper() not in db_cols_upper]
        assert not qy_cols_not_in_db_cols, f"column '{column}' invalid"
            

class Query:

    def __init__(self):
        self.util = Util()
        self.pkey = None
        self.cols = None


    def TABLE(self, table:str):
        """FROM Table"""
        self._query_string = ""
        self._query_table = table
        self.pkey = self.util.table_pkey(table)
        self.cols = self.util.table_cols(table)
        return self

    # -------------------------------- select -------------------------------- #
    @overload    
    def SELECT(self, column:str)->Self:
        ...
    @overload
    def SELECT(self, column:list|tuple)->Self:
        ...

    def SELECT(self, column="*")->Self:
        assert_column(column, self.cols, 'select')
        
        if isinstance(column, list) or isinstance(column, tuple):
            _query_select = f"SELECT {', '.join(column)} FROM {self._query_table}"
            self._query_string = self._query_string+_query_select
        elif isinstance(column, str):
            _query_select = f"SELECT {column} FROM {self._query_table}"
            self._query_string = self._query_string+_query_select
        else:
            raise NotImplementedError ('type not vaild')
        return self
    
    def WHERE(self, column:str, condition:Literal['IN','=','<','<=','>','=>'],data)->Self:
        return self._query_condition("WHERE", column, condition, data)

    def AND(self, column:str, condition:Literal['IN','=','<','<=','>','=>'],data)->Self:
        return self._query_condition("AND", column, condition, data)
        
    def OR(self, column:str, condition:Literal['IN','=','<','<=','>','=>'],data)->Self:
        return self._query_condition("OR", column, condition, data)

    def _query_condition(self, header, column, condition, data):
        assert_column(column, self.cols, 'condition')
    
        placeholder = "%s"
        if isinstance(data, list|tuple):
            placeholder = ', '.join(['%s'] * len(data))
        
        if condition == "IN":
            _query_filter = f"\n\t{header} " +f"{column} {condition} ({placeholder})"
        else:
            _query_filter = f"\n\t{header} " +f"{column} {condition} {placeholder}"
                
        self._query_string = self._query_string + _query_filter
        return self

    # --------------------------------- print -------------------------------- #
    @property
    def print(self):
        print(self._query_string)

    @property
    def summary(self):
        print(self.cols)
        print(self.pkey)

if __name__ == "__main__":
    query = Query()
    query.TABLE('raw_trade_data').summary
    query.TABLE('raw_trade_data').SELECT().print
    query.TABLE('raw_trade_data').SELECT(["time","symbol"]).print
    query.TABLE('raw_trade_data').SELECT(["time","symbol"]).WHERE('TIME',"IN",1).print
    query.TABLE('raw_trade_data').SELECT(["time","symbol"]).WHERE('TIME',"IN",[1,2,3,4,5]).print
    query.TABLE('raw_trade_data').SELECT(["time","symbol"]).WHERE('TIME',"IN",[1,2,3,4,5])\
        .AND('symbol','=','ABC').print