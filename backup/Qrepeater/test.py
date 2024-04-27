import threading

stop_event = threading.Event()

# print(f"stop_event: {stop_event.is_set()}")
# print(f"stop_event.wait: {stop_event.wait(2)}")
# cnt = 0
# while not stop_event.is_set():
#     cnt += 1
#     print(f"hi - {cnt}")
#     if cnt == 5:
#         stop_event.set()
#         print("stop_event set!")
#         print(f"stop_event: {stop_event.is_set()}")


import time
def func1():
    print(stop_event.wait(5))

def func2():
    print('hi')
    time.sleep(1)
    stop_event.set()

th1 = threading.Thread(target=func1)
th2 = threading.Thread(target=func2)

th1.start()
th2.start()

th1.join()


# def myfunc(x, *args):
#     print(x)
#     print(len(args))
#     if args:
#         print('ok')
#     else:
#         print('none')

# myfunc('hello')



# class A:


#     a = 1

#     class B:
#         def __init__(self, b):
#             self.b = b

#         def pp(self):
#             print(self.b)
#             print(self.a)
#     class C:
#         def __init__(self, c):
#             self.c = c

#         def pp(self):
#             print(self.c)


# b = A.B(3)
# b.pp()