from collections import namedtuple

# namedtuple 생성
Person = namedtuple('tt', ['name', 'age'])

# namedtuple 인스턴스 생성
p = Person(name='Alice', age=30)

# typename 접근 (클래스 이름)
typename = p.__class__.__name__

print(f"Typename: {typename}")