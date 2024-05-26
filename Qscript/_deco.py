def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Function is about to be called.")
        result = func(*args, **kwargs)
        print("Function has been called.")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}!")

# 함수 호출
say_hello("Alice")


class MyClass:
    @my_decorator
    def say_hello(self, name):
        print(f"Hello, {name}!")
obj = MyClass()
obj.say_hello("Alice")
# ---------------------------------------------------------------------------- #

def repeat(num_times):
    def decorator_repeat(func):
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat

@repeat(num_times=3)
def greet(name):
    print(f"Hello, {name}!")

# 함수 호출
greet("Alice")