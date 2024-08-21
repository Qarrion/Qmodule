import os
from typing import Literal
from configparser import ConfigParser

# -------------------------------- colorprint -------------------------------- #
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
			print(f"   ->> {m}")

# os.path.relpath(inipath1, os.getcwd())
# filepath = os.path.abspath(__file__)
# filedir = os.path.dirname(filepath)
# ---------------------------------------------------------------------------- #
class Config:
	"""
	>>> # example
	#----------------------------------[config.ini]
		[DEFAULT] # DEFAULT is common vars
		opt1 = 1
		opt2 = /home/%username%
		[logger]
		opt3 = text
	#----------------------------------------------
	config = Config('log.ini',debug=True)
	print(config.parser.get('logger', 'level'))
	print(config.parser.get('logger','fmt',raw=True))
	print(config.parser.get('logger','NoVar',fallback='fallback'))

	config.set_section('log')
	print(config.section.get('level'))
	print(config.section.get('fmt',raw=True))
	print(config.section.get('NoVar',fallback='fallback'))
	#----------------------------------------------
	# [DEFAULT] define 
	"""	
	def __init__(self, inifile, fallback='default.ini', debug=False) -> None:
		self._fallback = fallback
		self._filename = inifile
		self._debug = debug
		
		self.set_parser()

	def set_parser(self):
		self.parser = ConfigParser()
		inipaths = []
		inipaths.append(os.path.join(os.getcwd(),self._filename))
		inipaths.append(os.path.join(os.getcwd(),'config',self._filename))
		inipaths.append(os.path.join(os.path.dirname(__file__),self._fallback))

		for inipath in inipaths:
			dprint(f'config ({inipath})',rint:=os.path.isfile(inipath), self._debug)
			if rint :
				self.parser.read(inipath)
				self.is_default = 1 if self.parser.defaults() else 0
				if self.is_default:
					sections = ['DEFAULT']+self.parser.sections()
				else:
					sections = self.parser.sections()
				dprint(f"sections ('{"', '".join(sections)}')")
				return
		dprint(f"No config ({self._filename}).")

	def set_section(self, section=None):
		if section in self.parser.sections():
			self.section = self.parser[section]
			dprint(f"section ({section})",1)
		elif self.is_default:
			dprint(f"section ({section}->DEFAULT)",1)
			self.section = self.parser['DEFAULT']
		else:
			dprint(f"section ({section}->DEFAULT)",0)
			dprint(f"No section ({section} or DEFAULT)")
			return
		dprint(f"options ('{"', '".join(self.section.keys())}')")

		

if __name__ =="__main__":
	config = Config('log.ini',debug=True)
	print(config.parser.get('logger', 'level'))
	print(config.parser.get('logger','fmt',raw=True))
	print(config.parser.get('logger','NoVar',fallback='fallback'))

	config = Config('log.ini',debug=True)
	config.set_section('log')
	print(config.section.get('level'))
	print(config.section.get('fmt',raw=True))
	print(config.section.get('NoVar',fallback='fallback'))