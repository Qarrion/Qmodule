import sys
import random
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
import pyqtgraph as pg

class RealTimeCandlestickChart(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.enableAutoRange(x=True, y=True) # 자동 range (add)
        # self.setAutoVisible(x=True, y=True)  # 자동 min max
        # 차트 위젯 생성
        self.graphWidget = pg.PlotWidget(viewBox=ViewBox())

        self.setCentralWidget(self.graphWidget)

        # 초기 캔들스틱 데이터 생성
        self.data = [self.generate_candlestick_data(i) for i in range(10)]

        # 그래프 업데이트
        self.update_graph()

        # 타이머 설정
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1초 간격
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

    def generate_candlestick_data(self, x):
        # 임의의 캔들스틱 데이터 생성
        open = random.uniform(10, 20)
        close = open + random.uniform(-2, 2)
        low = min(open, close) - random.uniform(0, 2)
        high = max(open, close) + random.uniform(0, 2)
        return {'x': x, 'open': open, 'high': high, 'low': low, 'close': close}

    def update_data(self):
        # 데이터 업데이트
        self.data.append(self.generate_candlestick_data(len(self.data)))
        self.data.pop(0)

        # 그래프 업데이트
        self.update_graph()

    def update_graph(self):
        # 캔들스틱 그래프 업데이트
        self.graphWidget.clear()
        for d in self.data:
            color = 'r' if d['open'] > d['close'] else 'g'
            self.graphWidget.plot([d['x'], d['x']], [d['low'], d['high']], pen=color) # High/Low 선
            self.graphWidget.plot([d['x'], d['x']], [d['open'], d['close']], pen=color, symbolBrush=color) # Open/Close 막대

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=True, y=True) # 자동 range (add)
        self.setAutoVisible(x=False, y=True)  # 자동 min max

# 애플리케이션 실행
app = QApplication(sys.argv)
main = RealTimeCandlestickChart()
main.show()
sys.exit(app.exec())