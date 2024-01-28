import numpy as np

class ClassA:
    def __init__(self, array):
        self.array = array

    def update_array(self, new_values):
        self.array[:] = new_values

class ClassB:
    def __init__(self, array):
        self.array = array

# 공유될 numpy 배열 생성
shared_array = np.array([1, 2, 3])

# 두 클래스 인스턴스 생성, 동일한 배열 공유
instance_a = ClassA(shared_array)
instance_b = ClassB(shared_array)

instance_a.array
instance_b.array


shared_array = np.append(shared_array, np.array([1]))

# ClassA 인스턴스를 통해 배열 수정
instance_a.update_array([4, 5, 0])

# ClassB 인스턴스의 배열 확인
print("ClassB array:", instance_b.array)