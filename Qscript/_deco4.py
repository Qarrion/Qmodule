import time
from functools import wraps, update_wrapper
from inspect import signature

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 함수 실행 시간: {end_time - start_time} 초")
        return result
    # wrapper.__signature__ = signature(func)
    # update_wrapper(wrapper, func)
    return wrapper

@timer_decorator
def example_function(name):
    """이 함수는 예제 함수를 위한 것입니다."""
    time.sleep(2)
    print(f"Hello, {name}!")

example_function('dd')
print(example_function.__name__)  # example_function
print(example_function.__doc__)   # 이 함수는 예제 함수를 위한 것입니다.
# print(signature(example_function))  


# newfunc = timer_decorator(example_function)
# print(newfunc.__name__)  # examaple_function
# print(newfunc.__doc__)   # 이 함수는 예제 함수를 위한 것입니다.
# # print(signature(newfunc))  

import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 데코레이터가 추가로 수행할 작업을 여기서 수행합니다.
        print(f"Arguments were: {args}, {kwargs}")
        result = func(*args, **kwargs)
        # 결과값을 반환하거나 추가 작업을 여기서 수행합니다.
        return result
    return wrapper

@my_decorator
def say_hello(name, greeting="Hello"):
    """Greets a person with the given greeting."""
    return f"{greeting}, {name}!"

# 함수 호출 예시
print(say_hello("Alice"))
print(say_hello("Bob", greeting="Hi"))