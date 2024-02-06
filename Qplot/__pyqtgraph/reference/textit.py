import pyqtgraph as pg
from PySide6.QtWidgets import QApplication

app = QApplication([])
win = pg.GraphicsLayoutWidget(show=True) # 플롯 위젯 생성 및 표시

# 플롯 생성
plot = win.addPlot(title="텍스트 아이템 예제")

# 데이터 추가
x = [1, 2, 3, 4, 5]
y = [10, 20, 30, 40, 50]
plot.plot(x, y)

# TextItem 생성 및 추가
text = pg.TextItem("여기는 텍스트", color='red', anchor=(0, 0))
plot.addItem(text, ignoreBounds=True) # TextItem을 플롯에 추가

# 텍스트 위치 설정
text.setPos(3, 30)

app.exec()