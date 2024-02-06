# from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# from PySide6.QtWidgets import QApplication, QMainWindow
# import sys

# class Example(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         series = QLineSeries()
#         series.append(0, 6)
#         series.append(2, 4)
#         series.append(3, 8)
#         series.append(7, 4)
#         series.append(10, 5)

#         chart = QChart()
#         chart.addSeries(series)
#         chart.createDefaultAxes()

#         axisX = QValueAxis()
#         axisX.setRange(1, 11)  # 정수 범위 설정
#         axisX.setTickCount(11)  # 눈금 간격 설정 (0부터 10까지 11개의 눈금)
#         axisX.setMinorTickCount(2)  # 마이너 그리드 라인 비활성화
#         chart.setAxisX(axisX, series)

#         axisY = QValueAxis()
#         axisY.setRange(0, 10)
#         axisY.setTickCount(11)
#         axisY.setMinorTickCount(0)
#         chart.setAxisY(axisY, series)

#         chart_view = QChartView(chart)
#         self.setCentralWidget(chart_view)
#         self.resize(400, 300)
#         self.setWindowTitle('QValueAxis Example')

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     ex.show()
#     sys.exit(app.exec())


from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
import sys

class ChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        self.setRubberBand(QChartView.RectangleRubberBand)  # 확대/축소를 위한 고무 밴드 설정

    def wheelEvent(self, event):
        factor = 1.1
        if event.angleDelta().y() > 0:
            self.chart().zoom(factor)
        else:
            self.chart().zoom(1 / factor)

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        series = QLineSeries()
        series.append(0, 6)
        series.append(2, 4)
        series.append(3, 8)
        series.append(7, 4)
        series.append(10, 5)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()

        axisX = QValueAxis()
        axisX.setRange(0, 10)
        axisX.setTickCount(11)
        chart.setAxisX(axisX, series)

        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.setTickCount(11)
        chart.setAxisY(axisY, series)

        chart_view = ChartView(chart)
        self.setCentralWidget(chart_view)
        self.resize(400, 300)
        self.setWindowTitle('Interactive Zoom with Grid')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
