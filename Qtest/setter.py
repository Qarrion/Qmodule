import functools

class Wrapper:
    def __init__(self):
        self.functions = {}
 
    def set_fun(self, func):
        self.functions[func.__name__]= func
        return func
    
w = Wrapper()
# 테스트용 함수들
@w.set_fun
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
w.set_fun(fun2)


def fun3():
    """
    fun3 함수는 인수를 받지 않고 호출되며, 호출 메시지를 출력합니다.
    """
    print('fun3 called')


# Wrapper 클래스에 함수들을 넣어서 객체 생성

w.functions['fun1'](1)
# fun1(1)
fun1()

w.functions['fun2'](1,2)
fun2(1,2)