import time
import random

# 첫 번째 wrap 함수: 함수의 시작과 끝에 "start", "end"를 출력
def wrap_start_end(func):
    def wrapper(*args, **kwargs):
        print("w 1")
        print("start")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print("end")
            print("finally block executed")
            raise e  # 예외를 다시 던집니다
        finally:
            print("finally block executed")
        print("end")
        return result
    return wrapper

# 두 번째 wrap 함수: 오류 발생 시 3번까지 다시 실행
def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        print('w 2')
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < attempts:
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(1)  # 재시도 전에 1초 대기
                else:
                    print(f"Attempt {attempt} failed: {e}. No more retries.")
                    raise  # 마지막 시도에서도 실패하면 예외를 다시 던집니다
    return wrapper

# 테스트할 함수
@retry_on_exception
@wrap_start_end
def test_func():
    if random.choice([True, False]):
        raise ValueError("Random error occurred!")
    return "Success!"

# 함수 호출
try:
    print(test_func())
except Exception as e:
    print(f"Caught an exception: {e}")