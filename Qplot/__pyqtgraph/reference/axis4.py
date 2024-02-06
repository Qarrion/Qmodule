import pyqtgraph as pg
from PySide6.QtWidgets import QApplication
import numpy as np

class CustomAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(CustomAxis, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # 틱 문자열을 생성하는 부분
        strings = super(CustomAxis, self).tickStrings(values, scale, spacing)
        # 여기에서 각 틱 레이블에 대한 스타일을 적용할 수 있습니다.
        # 예를 들어, 모든 틱에 대해 배경색을 노란색으로 설정합니다.
        styled_strings = ['<span style="background-color: yellow;">{}</span>'.format(s) for s in strings]
        print(styled_strings)
        return styled_strings

app = QApplication([])

# 데이터 생성
x = np.linspace(0, 10, 1000)
y = np.sin(x)

# 그래프 위젯 생성
pw = pg.PlotWidget()

# 사용자 정의 AxisItem 추가
axis = CustomAxis(orientation='bottom')
pw.setAxisItems({'bottom': axis})

# 데이터 플롯
pw.plot(x, y)

pw.show()

app.exec()
