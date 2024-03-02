import tabulate
import pandas as pd
from typing import Literal

# pip install tabulate[widechars]
# pip install pandas as pd

def trim_text(text, limit):
    if isinstance(text,str) and len(text)>limit:
        text = text[:limit-3]+'...'
    return text

def table(dfr:pd.DataFrame, r=5, f:Literal["github","fancy_grid"]="github", w=15):
    """
        >>> r = rows    : 'num of rows'
        >>> f = format  : 'github', 'fancy_grid'
        >>> w = width   : 'max col widths = len of cols'
    """

    print(f'# of rows,cols : {dfr.shape[0]},{dfr.shape[1]}')
    dfr_h = dfr.head(r)
    dfr_t = dfr.tail(2)
    dfr_p = pd.concat([dfr_h,dfr_t])
    dfr_p = dfr_p.astype(str)
    
    if w is not None:
        dfr_p = dfr_p.map(lambda x:trim_text(x,w))

    idx = dfr_p.index.to_list() 
    idx[r]='...'
    dfr_p.index = idx
    dfr_p.iloc[r] = '...'


    dfr = dfr.astype(str)
    print(tabulate(dfr_p, headers='keys', tablefmt=f, maxcolwidths=w))

