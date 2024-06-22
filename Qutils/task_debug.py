# -------------------------------- ver 260622 -------------------------------- #
# split, xready
# ---------------------------------------------------------------------------- #
import asyncio, traceback, re
from collections import defaultdict
from datetime import datetime
# import textwrap

# task, group = all_tasks()
# self._custom.max(str(task))
# self._custom.max(str(group))

def split_long_string(s, chunk_size=100):
    # 문자열의 시작 위치
    start = 0
    # 문자열의 길이
    length = len(s)
    # 지정된 크기(chunk_size)로 분할하여 yield
    while start < length:
        yield s[start:start + chunk_size]
        start += chunk_size

class xdebug:

    @classmethod
    async def xready(self, sec=1):
        await asyncio.sleep(sed)

    @classmethod
    def set_main_task(self):
        asyncio.current_task().set_name('MAIN')
    
    @classmethod
    async def monitor(self, task_all:int=2):
        dtime_init = datetime.now()
        try:
            while True:
                await asyncio.sleep(1)
                await asyncio.sleep(task_all-1)
                task, group = self.all_tasks()
                group = " ".join(group)
                stime = self.str_timedelta(datetime.now()-dtime_init)
                head = f"\033[44m{stime}\033[0m "
                body = f"{'':>23}"
                text = f"\033[34m{str(task)} {str(group)}\033[0m"
                # w_text = textwrap.wrap(text, width=160)
                for i, t in enumerate(split_long_string(text,105)):
                    if i ==0:
                        print(f"{head}{t}")
                    else:
                        print(f"{body} ...{t}")        
            # print('1')
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! Monitor - Interrupted !! \033[0m")

    @classmethod
    async def gather(self, *args):
        try:
            await asyncio.gather(*args)
            # print('1')
        except asyncio.exceptions.CancelledError:
            print(f"\033[43m !! all task closed !! \033[0m")
            pass
        except Exception as e:
            print(e.__class__.__name__)
            traceback.print_exc()
            # print(f"\033[43m !! all task closed !! \033[0m")
    @classmethod
    async def cancel_all(self, sec):
        await asyncio.sleep(sec)
        [task.cancel() for task in asyncio.all_tasks()]

    @classmethod
    def all_tasks(self):
        tasks = asyncio.all_tasks()
        data = [task.get_name() for task in tasks]
        # print(data)
        # 사전을 사용하여 접두사별로 그룹화
        grouped_data = defaultdict(list)
        task_list = []

        for item in data:
            match = re.match(r'([a-zA-Z]+)-([\w-]+)', item)
            if match:
                prefix, suffix = match.groups()
                grouped_data[prefix].append(suffix)
            else:
                task_list.append(item)

        # 결과 문자열 생성
        GROUP = []
        TASK = []

        # 접두사별로 정렬하고 문자열 생성
        for prefix in sorted(grouped_data.keys()):
            # 문자와 숫자를 분리하여 정렬
            suffixes = grouped_data[prefix]
            numeric_suffixes = sorted([s for s in suffixes if s.isdigit()], key=int)
            non_numeric_suffixes = sorted([s for s in suffixes if not s.isdigit()])
            combined_suffixes = non_numeric_suffixes + numeric_suffixes
            combined_string = f"{prefix}-" + ",".join(combined_suffixes)
            combined_string = "["+combined_string+"]"
            GROUP.append(combined_string)

        # 숫자가 없는 항목 처리
        if task_list:
            TASK = sorted(task_list)

        return (TASK, GROUP)
    
    @classmethod
    def str_timedelta(self,tdelta):
        days = tdelta.days
        seconds = tdelta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"[{days:0>4}:D {hours:0>2}:H {minutes:0>2}:M {seconds:0>2}:S]"

