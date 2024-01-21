# https://toylee.net/pyqt6-qgraphicsview-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0/

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QValueAxis, QChartView, QLineSeries
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent

import numpy as np

class SimpleChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Chart Example")
        self.setGeometry(100, 100, 800, 600)

        # ------------------------------- Chart ------------------------------ #
        self.chart = QChart()
        self.chart.setTitle("Simple Line Chart")

        # ------------------------------ Series ------------------------------ #
        self.series = QLineSeries()
        self.series.setName("Line Chart")

        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 
        for i in range(len(x)):
                self.series.append(x[i], y[i])
        self.chart.addSeries(self.series)

        # ------------------------------- Axis ------------------------------- #
        self.axis_x = QValueAxis()
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setTickCount(5)
        self.axis_x.setTitleText("X-axis")
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%.1f")
        self.axis_y.setTickCount(6)
        self.axis_y.setTitleText("Y-axis")
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # ----------------------------- ChartView ---------------------------- #
        self.chart_view = ChartView(self.chart)
        self.setCentralWidget(self.chart_view)

        # -------------------------------------------------------------------- #
    
    def wheelEvent(self, event: QWheelEvent):
        # ------------------------------ RangeX ------------------------------ #
        x_max, x_min = self.axis_x.max(), self.axis_x.min()
        x_rng = (x_max - x_min) * 0.1

        if event.angleDelta().y() > 0:
            self.axis_x.setRange(x_min + x_rng , x_max)
        else:
            self.axis_x.setRange(x_min - x_rng , x_max)
        # ------------------------------ RangeY ------------------------------ #
        self._auto_scale_axis_y()

    def _auto_scale_axis_y(self):
        x_max, x_min = self.axis_x.max(), self.axis_x.min()
        y_min, y_max = float('inf'), float('-inf')
        for point in self.series.points():
            if x_min <= point.x() <= x_max:
                y_min = min(y_min, point.y())
                y_max = max(y_max, point.y())

        if y_min != float('inf') and y_max != float('-inf'):
            self.axis_y.setRange(y_min, y_max)

class ChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.isDragging = False
        # self.lastMousePosition = QPointF()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.isDragging = True
            self.lastMousePosition = event.position()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.isDragging:
            currentPosition = event.position()
            dx = currentPosition.x() - self.lastMousePosition.x()
            
            self.chart().scroll(-dx, 0)
            self.lastMousePosition = currentPosition
            self._auto_scale_axis_y()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.isDragging = False

    def _auto_scale_axis_y(self):
        x_max, x_min = self.chart().axes()[0].max(), self.chart().axes()[0].min()
        y_min, y_max = float('inf'), float('-inf')
        for point in self.chart().series()[0].points():
            if x_min <= point.x() <= x_max:
                y_min = min(y_min, point.y())
                y_max = max(y_max, point.y())

        if y_min != float('inf') and y_max != float('-inf'):
            self.chart().axes()[1].setRange(y_min, y_max)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = SimpleChart()
    window.show()
    sys.exit(app.exec())