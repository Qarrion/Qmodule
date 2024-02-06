import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QApplication, QPainter
from PySide6.QtWidgets import QMainWindow, QChartView
from PySide6.QtCharts import QtCharts

class ZoomPanChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Zoom and Pan Chart Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a chart and set general properties
        self.chart = QtCharts.QChart()
        self.chart.setTitle("Zoom and Pan Chart")

        # Create a line series for the chart
        self.series = QtCharts.QLineSeries()
        self.series.setName("Line Chart")

        # Add data points to the series
        for x in range(100):
            self.series.append(x, x * x)

        # Add the series to the chart
        self.chart.addSeries(self.series)

        # Create an axis for the X-axis
        self.axis_x = QtCharts.QValueAxis()
        self.axis_x.setLabelFormat("%.0f")
        self.axis_x.setTitleText("X-axis")

        # Create an axis for the Y-axis
        self.axis_y = QtCharts.QValueAxis()
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Y-axis")

        # Set the axes for the chart
        self.chart.setAxisX(self.axis_x, self.series)
        self.chart.setAxisY(self.axis_y, self.series)

        # Create a chart view and set the chart
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smooth lines

        # Enable zoom and pan interactions for the X-axis
        self.chart_view.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)
        self.chart_view.setInteractive(True)
        self.chart_view.setDragMode(QChartView.ScrollHandDrag)

        self.setCentralWidget(self.chart_view)

    def wheelEvent(self, event):
        factor = 1.1

        # 마우스 휠 방향에 따라 X축 줌 인/아웃
        if event.angleDelta().y() > 0:
            self.axis_x.setRange(self.axis_x.min() / factor, self.axis_x.max() / factor)
        else:
            self.axis_x.setRange(self.axis_x.min() * factor, self.axis_x.max() * factor)

        # Y축 높이를 X축 범위에 맞게 조정
        self.update_y_axis_range()

        # Redraw the chart
        self.chart_view.repaint()

    def update_y_axis_range(self):
        # X축 범위에 따라 Y축 높이를 조정
        x_min, x_max = self.axis_x.min(), self.axis_x.max()
        y_min = min([x * x for x in range(int(x_min), int(x_max) + 1)])
        y_max = max([x * x for x in range(int(x_min), int(x_max) + 1)])

        self.axis_y.setRange(y_min, y_max)
        # print(self.series.points())
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZoomPanChart()
    window.show()
    sys.exit(app.exec())