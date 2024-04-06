class Shared:
    a = 0

class A:
    def get_a(self):
        print(Shared.a)
    def set_a(self, a):
        Shared.a = a

class B:
    def get_a(self):
        print(Shared.a)
    def set_a(self, a):
        Shared.a = a



a=A()
b=B()
a.get_a()
b.get_a()
Shared.a=1
a.get_a()
b.get_a()

a.set_a(2)
a.get_a()
b.get_a()
b.set_a(3)
a.get_a()
b.get_a()