from Qsql.sql import Sql
from Qsql.query import Query

# 1. 일반적인 데이터 타입 및 대응 Python 타입:
# 정수형 (INTEGER, BIGINT 등): Python의 int를 사용합니다.
# 예: value = (12345,)
# 실수형 (REAL, DOUBLE PRECISION 등): Python의 float를 사용합니다.
# 예: value = (123.45,)
# 문자열 (VARCHAR, TEXT 등): Python의 str을 사용합니다.
# 예: value = ("example text",)
# 불리언 (BOOLEAN): Python의 bool을 사용합니다 (True 또는 False).
# 예: value = (True,) 또는 value = (False,)
# 날짜/시간 (DATE, TIMESTAMP 등): Python의 datetime.date나 datetime.datetime을 사용합니다.
# 예: import datetime; value = (datetime.date(2024, 1, 1),)
# 2. NULL 값 처리:
# PostgreSQL에서 NULL은 존재하지 않는 또는 알 수 없는 값을 나타냅니다. Python에서는 None을 사용하여 NULL을 나타냅니다. 따라서 어떤 컬럼이든 해당 값이 NULL이어야 한다면, Python에서는 None을 사용하면 됩니다.

# 예: 컬럼이 VARCHAR이고, 해당 값이 NULL이어야 한다면, value = (None,)으로 설정합니다.