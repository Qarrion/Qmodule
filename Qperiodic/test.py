from datetime import datetime, timedelta

def seconds_until_next_quarter_hour():
    """가장 가까운 15분까지 남은 초를 계산합니다."""
    now = datetime.now()
    # 현재 시간으로부터 다음 15분 단위 시간을 계산하기 위해 먼저 현재 분을 15로 나눈 나머지를 구합니다.
    minutes_past_quarter = now.minute % 15
    # 다음 15분 단위까지 남은 분을 계산합니다.
    minutes_to_next_quarter = 15 - minutes_past_quarter if minutes_past_quarter > 0 else 0
    # 다음 15분 단위 시간을 계산합니다.
    next_quarter_hour = now + timedelta(minutes=minutes_to_next_quarter - now.minute % 15, seconds=-now.second, microseconds=-now.microsecond)

    # 다음 15분 단위까지 남은 시간(초)을 계산합니다.
    return (next_quarter_hour - now).total_seconds()

# 함수 실행 및 결과 출력
seconds_until_next_quarter_hour()



def print_datetime(dtime:datetime):
    if isinstance(dtime,float):
        dt = datetime.fromtimestamp(dtime)
    elif isinstance(dtime,datetime):
        dt= dtime
    else:
        raise TypeError('invalid type')
    
    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    print(formatted_time)

def print_totalsec(seconds:float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = round(seconds-hours*3600-minutes*60,8)
    print(f"{hours:02d}:{minutes:02d}:{seconds}")

# def print_totalsec(seconds:float):
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     print(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}")
import time
time.time()
now = datetime.now()
every_minute =15
print_datetime(now)
if now.minute >= every_minute:
    tgt = now + timedelta(hours=1)
    tgt = tgt.replace(minute=every_minute,second=0,microsecond=0)
    print(tgt)
rslt = (tgt-now).total_seconds()
rslt
    
print_totalsec(rslt)

print_datetime(rslt)
dt
print(seconds_until_next_quarter_hour())