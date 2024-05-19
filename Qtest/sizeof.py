from pympler.asizeof import asizeof


v1 = '2020-01-01 00:00:00+09:00'
print(asizeof(v1))
v1 = '2020-01-01 00:00:00'
print(asizeof(v1))



from dateutil import parser
v2 = parser.parse(v1)
print(v2)
print(asizeof(v2))

# import pytz

# v3 = pytz.timezone('Asia/Seoul').localize(v2)
# print(v3)
# print(asizeof(v3))
