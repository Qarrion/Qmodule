import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------- #
#                                     event                                    #
# ---------------------------------------------------------------------------- #

# # ---------------------------------------------------------------------------- #
# _stop_event = threading.Event()
# print(_stop_event.is_set())
# # ---------------------------------------------------------------------------- #
# _stop_event.set()
# print(_stop_event.is_set())
# # ---------------------------------------------------------------------------- #
# _stop_event.clear()
# print(_stop_event.is_set())

# # ---------------------------------------------------------------------------- #
# print(_stop_event.wait(5)) # return False
# # ---------------------------------------------------------------------------- #
# def set_in_thread(event:threading.Event):
# 	time.sleep(1)
# 	print('set_in_thread')
# 	event.set()
# threading.Thread(target=set_in_thread, args=(_stop_event,)).start()
# print(_stop_event.wait(5)) # return True


# ---------------------------------------------------------------------------- #
#                                    signal                                    #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                               mainthread error                               #
# ---------------------------------------------------------------------------- #
from Qrepeater.utils.log_color import ColorLog
log_thread = ColorLog('log_thread','blue')
log_main = ColorLog('log_main','yellow')

def worker(sec):
	try:
		log_thread.info('start---------')
		time.sleep(sec)
		log_thread.info('----------done')
	except Exception as e:
		print(e)
stop = threading.Event()

with ThreadPoolExecutor(max_workers=3,thread_name_prefix='worker') as executor:
	while stop.wait(5) == False:
		log_main.info('---------------------------------------')
		futures = [executor.submit(worker,args=(i,)) for i in [1,2,3]]
		
		#! worker가 실행되기 전 오류 
		for future in as_completed(futures):
			try:
				future.result()
			except Exception as e:
				log_main.error(e)

# ---------------------------------------------------------------------------- #
#                              workerthread error                              #
# ---------------------------------------------------------------------------- #
# from Qrepeater.utils.log_color import ColorLog
# import random
# log_thread = ColorLog('log_thread','blue')
# log_main = ColorLog('log_main','yellow')

# def worker(sec):
# 	try:
# 		log_thread.info('start---------')
# 		if random.random() > 0.8:
# 			raise ValueError('raise error')
# 		time.sleep(sec)

# 		log_thread.info('----------done')
# 	except Exception as e:
# 		log_thread.error(e)
# stop = threading.Event()

# with ThreadPoolExecutor(max_workers=3,thread_name_prefix='worker') as executor:
# 	while stop.wait(2) == False:
# 		log_main.info('---------------------------------------')
# 		futures = [executor.submit(worker,i) for i in [1,2,3]]
		
# 		for future in as_completed(futures):
# 			try:
# 				future.result()
# 			except Exception as e:
# 				log_main.error(e)

# ---------------------------------------------------------------------------- #
#                                 timeout error                                #
# ---------------------------------------------------------------------------- #
# from Qrepeater.utils.log_color import ColorLog
# import random
# log_thread = ColorLog('log_thread','blue')
# log_main = ColorLog('log_main','yellow')

# def worker(sec):
# 	try:
# 		log_thread.info('start---------')
# 		# if random.random() > 0.8:
# 		# 	raise ValueError('raise error')
# 		time.sleep(sec)

# 		log_thread.info('----------done')
# 	except Exception as e:
# 		log_thread.error(e)
# stop = threading.Event()

# with ThreadPoolExecutor(max_workers=3,thread_name_prefix='worker') as executor:
# 	while stop.wait(2) == False:
# 		log_main.info('---------------------------------------')
# 		futures = [executor.submit(worker,i) for i in [1,2,5]]
		
# 		try:
# 			for future in as_completed(futures,timeout=1.1):
# 				try:
# 					future.result()
# 				except Exception as e:
# 					log_main.error(e)
# 		except TimeoutError:
# 			log_main.error('작업완료 초과')
# 			for future in futures:
# 				future.cancel()


