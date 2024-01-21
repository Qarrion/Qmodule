from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtCore import Qt, QPointF

class ChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.isDragging = False
        self.lastMousePosition = QPointF()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.isDragging = True
            self.lastMousePosition = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isDragging:
            currentPosition = event.position()
            dx = currentPosition.x() - self.lastMousePosition.x()
            dy = currentPosition.y() - self.lastMousePosition.y()
            self.chart().scroll(-dx, dy)
            self.lastMousePosition = currentPosition

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.isDragging = False

app = QApplication([])

series = QLineSeries()
series.append(0, 6)
series.append(2, 4)
series.append(3, 8)
series.append(7, 4)
series.append(10, 5)

chart = QChart()
chart.addSeries(series)
chart.createDefaultAxes()

chart_view = ChartView(chart)

window = QMainWindow()
window.setCentralWidget(chart_view)
window.resize(400, 300)
window.show()

app.exec()