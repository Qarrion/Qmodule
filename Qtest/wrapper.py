
import functools 

def hook(func):
    functools.wraps(func)
    def wrapper(*args, limit=True, **kwargs):
        if limit:
            print('limit start')
            rslt= func(*args, **kwargs)
            print('limit finish')
        else:
            print('origin')
            rslt=func(*args, **kwargs)
        
        return rslt
    
    return wrapper

@hook
def ofunc(x):
    return x+2

ofunc(1,limit=False)

# wfun=hook(ofunc)


# wfun()