
import re, asyncio
from collections import defaultdict

def all_tasks():
    tasks = asyncio.all_tasks()
    data = [task.get_name() for task in tasks]
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
        GROUP.append(combined_string)

    # 숫자가 없는 항목 처리
    if task_list:
        TASK = sorted(task_list)

    return (TASK, GROUP)


if __name__ == "__main__":

    data = ['Task-7', 'worker-7', 'worker-9', 'Task-10', 'worker-8', 'worker-10', 'worker-9', 
            'Task-11', 'worker-1', 'worker-10', 'worker-2', 'worker-2', 'Task-1', 'worker-3', 'worker-a'
            'Task-8', 'worker-1', 'Task-2', 'worker-4', 'worker-3', 'OFFSET', 'Task-9', 'worker-5', 'worker-ms',
            'worker-4', 'DIVIDER', 'worker-6', 'worker-5', 'Task-5', 'worker-7', 'worker-6', 'Task-6', 'worker-8']

    TASK, GROUP = all_tasks()
    print("TASK:", TASK)
    print("GROUP:", GROUP)