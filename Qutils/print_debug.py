from typing import Literal








def dprint(m, c=Literal[0,1], d=True):
	"m:msg, c:color, d:debug"
	name = ['green', 'red', 'reset']
	shell = "\033[32m", "\033[31m", "\033[0m"
	cmap = dict(zip(name, shell))
	# print(f"{cmap[color]}{msg}{cmap['reset']}")
	if d:
		if c == 1:
			print(f"{cmap['green']}[1]->> {m}{cmap['reset']}")
		elif c == 0:
			print(f"{cmap['red']}[0]->> {m}{cmap['reset']}")
		else:
			print(m)