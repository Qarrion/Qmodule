import tabulate
import pandas as pd
from typing import Literal

# pip install tabulate[widechars]
# pip install pandas as pd
def table(self, dfr:pd.DataFrame, r=6, f:Literal["github","fancy_grid"]="github", w=None):
    """
        >>> r = rows    : 'num of rows'
        >>> f = format  : 'github', 'fancy_grid'
        >>> w = width   : 'max col widths = len of cols'
    """

    print(f'# of rows,cols : {dfr.shape[0]},{dfr.shape[1]}')
    print(tabulate(dfr.head(r), headers='keys', tablefmt=f, maxcolwidths=w))

