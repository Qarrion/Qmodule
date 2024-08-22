import functools

def create_wrapper_class(**kwargs):
    class Wrapper:
        def __init__(self):

            
            for name, func in kwargs.items():
                wrapped_func = self._wrap_function(func)
                setattr(self, name, wrapped_func)

        def _wrap_function(self, func):
            @functools.wraps(func)
            def wrapped_function(*args, **kwargs):
                print('hi')
                result = func(*args, **kwargs)
                print('bye')
                return result
            return wrapped_function

    return Wrapper

# 테스트용 함수들
def fun1(x):
    """
    fun1 함수는 하나의 인수를 받아들이고 그 인수를 출력합니다.
    :param x: 인수
    """
    print(f'fun1 called with {x}')

def fun2(x, y):
    """
    fun2 함수는 두 개의 인수를 받아들이고 그 인수들을 출력합니다.
    :param x: 첫 번째 인수
    :param y: 두 번째 인수
    """
    print(f'fun2 called with {x} and {y}')

def fun3():
    """
    fun3 함수는 인수를 받지 않고 호출되며, 호출 메시지를 출력합니다.
    """
    print('fun3 called')

# Wrapper 클래스 생성
Wrapper = create_wrapper_class(fun1=fun1, fun2=fun2, fun3=fun3)

# Wrapper 클래스 인스턴스 생성
wrapped_functions = Wrapper()

# 클래스의 메서드로 함수 실행
wrapped_functions.fun1(10)
wrapped_functions.fun2(20, 30)
wrapped_functions.fun3()

wrapped_functions.fun1




print(dir(wrapped_functions))
wrapped_functions.fun1()