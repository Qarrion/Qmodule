# -------------------------------- ver 260622 -------------------------------- #
# split, xready
# ---------------------------------------------------------------------------- #

import asyncio, traceback, re, time
from collections import defaultdict
from datetime import datetime

async def xready(sec=1):
    await asyncio.sleep(sec)

def set_main_task(name = 'MAIN'):
    asyncio.current_task().set_name(name)

async def xmonitor(task_all:int=2,msg_count=True):
    dtime_init = datetime.now()
    try:
        while True:
            for _ in range(task_all):
                await asyncio.sleep(1)

            task, group = get_all_tasks(msg_count=msg_count)
            
            group = " ".join(group)
            stime = _str_timedelta(datetime.now()-dtime_init)
            head = f"\033[44m{stime}\033[0m "
            body = f"{'':>23}"
            text = f"\033[34m{str(task)} {str(group)}\033[0m"

            for i, t in enumerate(_split_long_string(text,110)):
                if i ==0:
                    print(f"{head}{t}")
                else:
                    print(f"{body} ...{t}")        

    except asyncio.exceptions.CancelledError:
        print(f"\033[43m !! Monitor - Interrupted !! \033[0m")

async def xgather(*args):
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

def callback_cancel_all(future):
    [task.cancel() for task in asyncio.all_tasks()]

def get_all_tasks(msg_count=True):
    """return (TASK, GROUP)"""

    tasks = asyncio.all_tasks()
    data = [task.get_name() for task in tasks]

    grouped_data = defaultdict(list)
    task_list = []

    for item in data:
        match = re.match(r'([a-zA-Z]+)-([\w-]+)', item)
        if match:
            prefix, suffix = match.groups()
            grouped_data[prefix].append(suffix)
        else:
            task_list.append(item)

    GROUP = []
    TASK = []

    for prefix in sorted(grouped_data.keys()):
        # 문자와 숫자를 분리하여 정렬
        suffixes = grouped_data[prefix]

        numeric_suffixes = sorted([s for s in suffixes if s.isdigit()], key=int)
        non_numeric_suffixes = sorted([s for s in suffixes if not s.isdigit()])
        if msg_count:
            numeric_suffixes = [f"({len(numeric_suffixes)})"]
        combined_suffixes = non_numeric_suffixes + numeric_suffixes
        combined_string = f"{prefix}-" + ",".join(combined_suffixes)
        combined_string = "["+combined_string+"]"
        GROUP.append(combined_string)

    # 숫자가 없는 항목 처리
    if task_list:
        TASK = sorted(task_list)

    return (TASK, GROUP)


# ----------------------------------- util ----------------------------------- #
def _split_long_string(text, chunk_size=100):
    # 문자열의 시작 위치
    start = 0
    # 문자열의 길이
    length = len(text)
    # 지정된 크기(chunk_size)로 분할하여 yield
    while start < length:
        yield text[start:start + chunk_size]
        start += chunk_size

def _str_timedelta(tdelta):
    days = tdelta.days
    seconds = tdelta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"[{days:0>4}:D {hours:0>2}:H {minutes:0>2}:M {seconds:0>2}:S]"