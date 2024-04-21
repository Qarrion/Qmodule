from typing import Literal
import logging

cmap = dict(
	reset = "\033[0m",
	red = "\033[31m",
	green = "\033[32m",
	yellow = "\033[33m",
	blue = "\033[34m",
	purple = "\033[35m",
	cyan = "\033[36m",
	white = "\033[37m")

def ColorLog(name, color:Literal['red','green','yellow','blue','purple']):
	# 로그 핸들러 생성
	handler = logging.StreamHandler()
	handler.setLevel(logging.DEBUG)

	# 로그 포맷 설정
 
	formatter = logging.Formatter(
		f"{cmap[color]}%(asctime)s | %(levelname)-7s | %(name)-7s | %(message)-40s | [%(threadName)s]{cmap['reset']}"
	)
	handler.setFormatter(formatter)

	# 로거 생성
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)

	return logger


if __name__ == "__main__":

	logger = ColorLog('test','blue')
	# 로그 메시지 출력
	logger.debug("debug message")
	logger.info("info message")
	logger.warning("warning message")
	logger.error("error message")
	# logger.critical("critical message")