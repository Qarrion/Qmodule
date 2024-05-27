# import functools

# class CallCounter:
#     def __init__(self, func):
#         self.func = func
#         self.count = 0
#         functools.wraps(func)(self)

#     def __call__(self, *args, **kwargs):
#         self.count += 1
#         print(f"Call {self.count} of {self.func.__name__}")
#         return self.func(*args, **kwargs)

# # 데코레이터 사용 예시
# @CallCounter
# def say_hello(name):
#     print(f"Hello, {name}!")

# # 함수 호출
# say_hello("Alice")

# say_hello("Bob")



# import functools

# class PreserveMeta:
#     def __init__(self, func):
#         self.func = func
#         functools.update_wrapper(self, func)

#     def __call__(self, *args, **kwargs):
#         # 여기서 추가 기능을 구현할 수 있습니다.
#         print(f"Calling {self.func.__name__} with args: {args} and kwargs: {kwargs}")
#         return self.func(*args, **kwargs)

# # 데코레이터 사용 예시
# @PreserveMeta
# def example_function(param1, param2):
#     """
#     This is an example function.

#     Args:
#         param1 (str): The first parameter.
#         param2 (int): The second parameter.

#     Returns:
#         str: A formatted string combining param1 and param2.
#     """
#     return f"{param1} is combined with {param2}"

# # 함수 호출
# print(example_function("Hello", 42))

# # 함수의 문서 문자열 출력
# print(example_function.__doc__)



# def my_decorator(func):
#     def wrapper():
#         print("함수가 호출되기 전에 실행됩니다.")
#         func()
#         print("함수가 호출된 후에 실행됩니다.")
#     return wrapper

# @my_decorator
# def say_hello(a):
#     print(f"Hello! {a}")


# say_hello()


import asyncio
from functools import wraps
class A:
    def my_decorator(self, func, a=2):
        wraps(func)
        async def wrapper(*args, **kwargs):
            print("함수가 호출되기 전에 실행됩니다.")
            rslt = await func(*args, **kwargs)
            print("함수가 호출된 후에 실행됩니다.")
            return rslt
        return wrapper

a = A()

@a.my_decorator
async def say_hello2(a):
    print(f"Hello! {a}")

asyncio.run(say_hello2('a'))