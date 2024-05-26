


class MyClass:
    def set_func(self, func):
        self.func = func
obj = MyClass()


def local_func(name):
    print(f"hi {name}")

obj.set_func(local_func)
obj.func('kim')


@obj.set_func
def local_func(name):
    print(f"hi {name}")

obj.func('kim')

# ---------------------------------------------------------------------------- #
from functools import wraps

class MyClass:
    def set_func(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Wrapper: Before calling the function")
            result = func(*args, **kwargs)
            print("Wrapper: After calling the function")
            return result
        self.func = wrapper

obj = MyClass()

# def local_func(name):
#     """This function says hi to the given name."""
#     print(f"hi {name}")

# obj.set_func(local_func)
# obj.func('kim')

@obj.set_func
def local_func(name):
    """This function says hi to the given name."""
    print(f"hi {name}")
obj.func('kim')