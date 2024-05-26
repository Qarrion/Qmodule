def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()

# ---------------------------------------------------------------------------- #
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Something is happening before the function is called.")
        result = func(*args, **kwargs)
        print("Something is happening after the function is called.")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")

# ---------------------------------------------------------------------------- #
def decorator1(func):
    def wrapper():
        print("Decorator 1")
        func()
    return wrapper

def decorator2(func):
    def wrapper():
        print("Decorator 2")
        func()
    return wrapper

@decorator1
@decorator2
def say_hello():
    print("Hello!")

say_hello()
# ---------------------------------------------------------------------------- #
def method_decorator(func):
    def wrapper(self, *args, **kwargs):
        print("Method decorator is being called")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @method_decorator
    def say_hello(self):
        print("Hello from the class!")

obj = MyClass()
obj.say_hello()