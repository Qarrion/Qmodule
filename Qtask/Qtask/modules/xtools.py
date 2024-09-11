# -------------------------------- ver 260622 -------------------------------- #
# split, xready
# -------------------------------- ver 260713 -------------------------------- #
# task_log,xinterrupt
# ---------------------------------------------------------------------------- #
import asyncio, traceback, re, time
from collections import defaultdict
from datetime import datetime
from typing import Literal
from Qlogger import Logger

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

class Xtools:

    def __init__(self, name:str='xtools',msg=True):
        self._logger = Logger(clsname='Xtools', logname=name)
        self._dtime_init = datetime.now()

        # self.worker_to_task = ['pgsql-scheduler']
        self.worker_to_task = ['']
        self.replace = {
            'pgsql-worker':'pgsql'
        }
        self._pool=None
    # ------------------------------------------------------------------------ #
    #                               function_task                              #
    # ------------------------------------------------------------------------ #
    async def xmonitor(self, tasks:int=60, reapet:int=2, pool=None):
        self._pool = pool
        try:
            while True:
                for _ in range(int(tasks/reapet)):
                    await asyncio.sleep(reapet)
                # ------------------------------------------------------------ #
                # dd = self.get_taskdict()
                # print(dd)
                self.status_tasks()
                # ------------------------------------------------------------ #
                # self.log_all_tasks()

        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! Monitor - Interrupted !! \033[0m")
            [task.cancel() for task in asyncio.all_tasks()]
            
    def callback_cancel_all(self, future):
        [task.cancel() for task in asyncio.all_tasks()]

    def set_main_task(self, name = 'MAIN'):
        asyncio.current_task().set_name(name)

    async def xready(self, sec=1):
        await asyncio.sleep(sec)

    async def xgather(self, *args):
        try:
            await asyncio.gather(*args)
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! all task closed !! \033[0m")
            
        except Exception as e:
            print(e.__class__.__name__)
            traceback.print_exc()
    # ------------------------------------------------------------------------ #
    #                                status_task                               #
    # ------------------------------------------------------------------------ #
    def get_taskdict(self):
        taskdict = defaultdict(list)
        tasks = asyncio.all_tasks()
        all_tasks = [task.get_name() for task in tasks]
        # print(all_tasks)

        for name in all_tasks:
            # match = re.match(r'([\w]+)-([\w-]+)', name)
            # match = re.match(r'(.+)-([^-]+)$', name)
            # match = re.match(r'(.+)-(\d+)$', name)
            if name.startswith('pgsql-worker'):
                name = name.replace('pgsql-worker','pgsql')
            
            match = re.match(r'(.+)-(\w+)$', name)
            if name in self.worker_to_task:
                taskdict['MAIN'].append(name)
                
            elif match:
                prefix, suffix = match.groups()
                taskdict[prefix].append(suffix)
            else:
                taskdict['MAIN'].append(name)
        return taskdict
    
    def status_tasks(self, mode:Literal['list','number']='number', width=125):
        # 2024-08-11 08:03:02,738 | INFO    | Pool..........(Pool) | pool.............ini | ---------------------------------------------Pool |
        # [0000:D 00:H 00:M 04:S] |  MAIN   |  ['entry1', 'entry2'] [Task-1, 2]                                                               |
        task_dict = self.get_taskdict()
        msg_runtime = self._str_timedelta()
        len_runtime = len(msg_runtime)
        msg_empty = f"{" ":>{len_runtime}}"

        msg_main = self._gen_msg_main(task_dict, mode='list')
        msg_work = self._gen_msg_work(task_dict, mode=mode)

        # ------------------------------- print ------------------------------ #

        cprint(f"{msg_runtime} | {"TASK":<7} | {msg_main:<{width}} |",color='cyan')
        for msg_w in self._split_long_string(msg_work, chunk_size=width):
            cprint(f"{msg_empty} | {"WORKER":<7} | {msg_w:<{width}} |",color='cyan')
        
        if self._pool is not None:
            cprint(f"{msg_empty} | {"POOL":<7} | {self._pool._str_pool():<{width}} |",color='cyan')
    # | Collect.......[collect] | Task-1.xupdate_candl*() | KRW-BLUR               , 23.06.27 15:05 (to)    , [done - no data]        |
    # ------------------------------------------------------------------------ #
    #                                  message                                 #
    # ------------------------------------------------------------------------ #
    def _gen_msg_main(self, task_dict, mode:Literal['list','number']='list'):
        msg=''
        if 'MAIN' in task_dict:
            str_main =str(task_dict['MAIN'])
            str_main= f"[{'], ['.join(task_dict['MAIN'])}], "
            msg = msg+str_main

        if 'Task' in task_dict:
            str_task= self._tasks_to_str(prefix='Task', suffix_list=task_dict['Task'], mode=mode)
            msg = msg+str_task

        return msg

    def _gen_msg_work(self, task_dict, mode:Literal['list','number']='number'):
        keys = list(task_dict.keys())
        keys = sorted([k for k in keys if k not in ['MAIN','Task']])
        msg_list = []
        for k in keys:
            msg_list.append( self._tasks_to_str(k, task_dict[k], mode))

        msg_task = ", ".join(msg_list)
        return msg_task
    
    def _tasks_to_str(self, prefix:str, suffix_list:list, mode:Literal['list','number']):
        num_suffix_list = sorted([str(s) for s in suffix_list if s.isdigit()])
        str_suffix_list = sorted([str(s) for s in suffix_list if not s.isdigit()])

        if mode == "list":
            sorted_suffix_list = str_suffix_list + num_suffix_list
            str_task= f"[{prefix}]-({', '.join(sorted_suffix_list)})"
    
        elif mode == "number":
            if len(num_suffix_list) != 0 :
                num_suffix_list=[f"#{len(num_suffix_list)}"]
                sorted_suffix_list = str_suffix_list + num_suffix_list
            else:
                sorted_suffix_list = str_suffix_list
            str_task= f"[{prefix}]-({', '.join(sorted_suffix_list)})"

        return str_task
    
    def _split_long_string(self, text, chunk_size=100):
        # 문자열의 시작 위치
        start = 0
        # 문자열의 길이
        length = len(text)
        # 지정된 크기(chunk_size)로 분할하여 yield
        while start < length:
            yield text[start:start + chunk_size]
            start += chunk_size

    def _str_timedelta(self, tdelta=None):
        if tdelta is None:
            tdelta = datetime.now()-self._dtime_init
        days = tdelta.days
        seconds = tdelta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        # return f"\033[44m[{days:0>4}:D {hours:0>2}:H {minutes:0>2}:M {seconds:0>2}:S]\033[0m "
        return f"[{days:0>4}:D {hours:0>2}:H {minutes:0>2}:M {seconds:0>2}:S]"



if __name__ == "__main__":
# 2024-08-11 08:04:00,833 | INFO    | Pool..........(Pool) | pool.............ini | ---------------------------------------------Pool |
# [0000:D 00:H 00:M 04:S]
    xtools = Xtools()

    async def work1():
        while True:
            print(asyncio.current_task().get_name(), 'start')
            await asyncio.sleep(3)
            print(asyncio.current_task().get_name(), 'end')

    async def worker1():
        async with asyncio.TaskGroup() as tg:
            tg.create_task(work1(),name='worker1-1')
            tg.create_task(work1(),name='worker1-2')
            tg.create_task(work1(),name='worker1-3')

    async def worker2():
        tasks = [
            asyncio.create_task(work1(),name='run-M'),
            asyncio.create_task(work1(),name='run-Server'),
            asyncio.create_task(work1(),name='run-A'),
            asyncio.create_task(work1(),name='run-1-1'),
            asyncio.create_task(work1(),name='run-S-1'),
            asyncio.create_task(work1(),name='run-1'),
            asyncio.create_task(work1(),name='run-1-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-S-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-5-1'),
            asyncio.create_task(work1(),name='run-6-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-9-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1'),
            asyncio.create_task(work1(),name='run-4-1')
        ]
        await asyncio.gather(*tasks)

    async def main():

        monitor = asyncio.create_task(xtools.xmonitor(2))
        task1 = asyncio.create_task(worker1(),name='entry1')
        task2 = asyncio.create_task(worker2(),name='entry2')  

        await asyncio.gather(task1,task2,monitor) 


    asyncio.run(main())