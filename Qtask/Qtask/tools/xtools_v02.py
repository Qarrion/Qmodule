# -------------------------------- ver 260622 -------------------------------- #
# split, xready
# ---------------------------------------------------------------------------- #
import asyncio, traceback, re, time
from collections import defaultdict
from datetime import datetime
from Qtask.utils.logger_custom import CustomLog


class Xtools:

    def __init__(self, name:str='xtools',msg=True):
        CLSNAME = 'Xtool'
        try:
            from Qlogger import Logger
            logger = Logger(name, 'blue')
        except ModuleNotFoundError as e:
            logger = None
            print(f"\033[31m No Module Qlogger \033[0m")

        self._custom = CustomLog(logger, CLSNAME, 'async')
        if msg : self._custom.info.ini(name)

        self._balancer = dict()

    def set_balancer(self, *args):
        for b in args:
            self._balancer[b._name] = b

    def _taskname_to_taskdict(self):
        """
        >>> # tasks
        match = re.match(r'([\w]+)-([\w-]+)', name)
        prefix, suffix = match.groups()

        + dict[prefix] = suffix
        + dict['prefix'] = name
        """

        tasks = asyncio.all_tasks()
        data = [task.get_name() for task in tasks]

        result = defaultdict(list)

        for name in data:
            match = re.match(r'([\w]+)-([\w-]+)', name)
            if match:
                prefix, suffix = match.groups()
                result[prefix].append(suffix)
            else:
                result['prefix'].append(name)

        return result
    
    def _taskdict_to_text(self,taskdict:dict, suffix_len=True):
        TASKS = []
        GROUP = []
        for prefix in sorted(taskdict.keys()):
        # for prefix in taskdict:
            if prefix == "prefix":
                TASKS = sorted(taskdict["prefix"])

            else:
                suffix_list = sorted(taskdict[prefix])
                num_suffix_list = sorted([s for s in suffix_list if s.isdigit()])
                str_suffix_list = sorted([s for s in suffix_list if not s.isdigit()])
                
                if suffix_len:
                    if prefix in self._balancer:
                        load = self._balancer[prefix].get_load()
                        num_suffix_list = [f"({load}/{len(num_suffix_list)})"]
                    else:
                        num_suffix_list = [f"({len(num_suffix_list)})"]

                suffix_list = str_suffix_list + num_suffix_list
                
                GROUP.append(f"[{prefix}-{','.join(suffix_list)}]")

        TASK_TEXT =  f" TASKS | [{'], ['.join(TASKS)}]"
        GROUP_TEXT = f" GROUP | {', '.join(GROUP)}"

        return (TASK_TEXT, GROUP_TEXT)

    async def xmonitor(self, reapet:int=2):
        try:
            while True:
                for _ in range(reapet):
                    await asyncio.sleep(1)
                taskdict = self._taskname_to_taskdict()
                TASK,GROUP = self._taskdict_to_text(taskdict)
                self._custom.info.max(TASK)
                self._custom.info.max(GROUP)
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! Monitor - Interrupted !! \033[0m")

    # --------------------------------- util --------------------------------- #
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
            pass
        except Exception as e:
            print(e.__class__.__name__)
            traceback.print_exc()

if __name__ == "__main__":

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
            asyncio.create_task(work1(),name='run-S'),
            asyncio.create_task(work1(),name='run-A'),
            asyncio.create_task(work1(),name='run-1'),
            asyncio.create_task(work1(),name='run-4')
        ]
        await asyncio.gather(*tasks)

    async def main():

        monitor = asyncio.create_task(xtools.xmonitor(2))
        task1 = asyncio.create_task(worker1(),name='entry1')
        task2 = asyncio.create_task(worker2(),name='entry2')  

        await asyncio.gather(task1,task2,monitor) 


    asyncio.run(main())