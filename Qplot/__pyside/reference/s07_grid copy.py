import sys
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class ChartView(QChartView):
    def __init__(self, chart, axisX, axisY):
        super().__init__(chart)
        self.setRubberBand(QChartView.RectangleRubberBand)  # 확대/축소를 위한 고무 밴드 설정
        self.axisX = axisX
        self.axisY = axisY

    def wheelEvent(self, event):
        factor = 1.1
        if event.angleDelta().y() > 0:
            self.chart().zoom(factor)
        else:
            self.chart().zoom(1 / factor)
        self.updateAxisRange()

    def updateAxisRange(self):
        plotArea = self.chart().plotArea()
        xMin = self.chart().mapToValue(plotArea.topLeft()).x()
        xMax = self.chart().mapToValue(plotArea.bottomRight()).x()
        yMin = self.chart().mapToValue(plotArea.bottomLeft()).y()
        yMax = self.chart().mapToValue(plotArea.topRight()).y()

        self.axisX.setRange(xMin, xMax)
        self.axisY.setRange(yMin, yMax)
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

        axisX = QValueAxis()
        axisX.setRange(0, 10)
        axisX.setTickCount(2.4)
        chart.addAxis(axisX, Qt.AlignBottom)  # 축을 차트에 추가
        series.attachAxis(axisX)  # 시리즈에 X 축 연결

        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.setTickCount(11)
        chart.addAxis(axisY, Qt.AlignLeft)  # 축을 차트에 추가
        series.attachAxis(axisY)  # 시리즈에 Y 축 연결

        chart_view = ChartView(chart, axisX, axisY)
        self.setCentralWidget(chart_view)
        self.resize(400, 300)
        self.setWindowTitle('Interactive Zoom with Grid Update')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())