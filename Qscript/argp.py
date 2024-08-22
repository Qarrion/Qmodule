## argparse 설치 및 import
import argparse

## argument를 받기 위한 객체 만들기
parser = argparse.ArgumentParser()

## 객체에 argument 추가하기

### 필수 argument 추가
parser.add_argument('arg_A', type=int) # type이 int인 arg_A 이름의 필수 인자 추가
parser.add_argument('arg_B', type=str) # type이 str인 arg_B 이름의 필수 인자 추가

### 옵셧 argument 추가
parser.add_argument('-C', '--arg_C', type=str, default='cocoa')
# type이 str인 arg_C 이름(약어 C)인 옵션 인자 추가(미입력시 초기값 cocoa)

## argument 분석
args = parser.parse_args()

print("arg는 뭘까?")
print(args)