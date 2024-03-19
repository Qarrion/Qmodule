



def myfunc(a,b,c):
    print("a",a)
    print("b",b)
    print("c",c)


def outer(args=(),kwargs={}):
    myfunc(*args, **kwargs)

# outer((1,2),{'c':5})
# outer((1,2,3),{})

import sys

print(sys.getsizeof(()))



from functools import partial

def wrapper(fun, args, kwargs):
    return partial(fun,*args,**kwargs)


wrapper(myfunc, args=(1,2),kwargs={"c":5})()