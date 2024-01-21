from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QLineSeries
from PySide6.QtCore import QTimer, Slot
from PySide6.QtGui import QPainter
import sys
import random

class LiveChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        # 차트 시리즈 생성
        self.series = QLineSeries()
        
        # 차트 설정
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self._axisX = QValueAxis()
        self._axisY = QValueAxis()
        # self.chart.setAnimationOptions(QChart.AllAnimations)

        # 차트 뷰 설정
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.chart_view)

        # 데이터 업데이트 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(500)  # 데이터 업데이트 주기 (예: 1000ms)

    @Slot()
    def update_data(self):
        # 새로운 데이터 포인트 추가
        x = self.series.count()
        y = random.random()   # 예시 데이터
        print(x,y)
        self.series.append(x, y)
        # self.chart.createDefaultAxes()
        # self.chart.update()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveChartWindow()
    window.show()
    app.exec()
        # 차트 뷰 업데이트
        # self.chart.removeSeries(self.series)
        # self.chart.addSeries(self.series)
        # self.chart.createDefaultAxes()