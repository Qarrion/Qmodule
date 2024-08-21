from typing import Literal

# https://misc.flogisoft.com/bash/tip_colors_and_formatting

# "\033[32m  \033[0m"
# "\033[31m  \033[0m"

cmap = dict(
	reset = "\033[0m",
	red = "\033[31m",
	green = "\033[32m",
	yellow = "\033[33m",
	blue = "\033[34m",
	purple = "\033[35m",
	cyan = "\033[36m",
	white = "\033[37m",
	
    red_ = "\033[41m",
	green_ = "\033[42m",
	yellow_ = "\033[43m",
	blue_ = "\033[44m",
	purple_ = "\033[45m",
	cyan_ = "\033[46m",
	white_ = "\033[47m",
    )

hint = Literal['red','green','yellow','blue','purple','cyan','white','_']

def cprint(msg, color:hint):
    print(f"{cmap[color]}{msg}{cmap['reset']}")

if __name__ == "__main__":
    cprint('hi','green')
    cprint('hi','red')
    cprint('gi','blue_')
