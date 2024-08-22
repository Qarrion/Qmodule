from typing import Literal


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

def dprint(msg, status, debug=True):
	if debug:
		if status == 1:
			print(f"{cmap['green']}[1]->> {msg}{cmap['reset']}")
		elif status == 0:
			print(f"{cmap['red']}[0]->> {msg}{cmap['reset']}")
		else:
			print(f"   ->> {msg}")

eprint = lambda x,n=80: print(f"{"="*n} [{x}]")

if __name__ == "__main__":
    
	cprint('hi','blue')
	dprint('hi',0)
	dprint('hi',1)
	eprint('hi')