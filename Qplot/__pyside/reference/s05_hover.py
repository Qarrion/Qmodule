import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsLineItem, QToolTip
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QMouseEvent, QPen

class ChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        # 차트와 시리즈 생성
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)

        # 차트 뷰 생성 및 설정
        self.chart_view = ChartView(self.chart)
        self.setCentralWidget(self.chart_view)

        # 데이터 추가 (예시)
        self.series.append(0, 6)
        self.series.append(2, 4)
        self.series.append(3, 8)
        self.series.append(7, 13)
        self.series.append(10, 5)

        self.chart.createDefaultAxes()
        self.chart.axes(Qt.Horizontal)[0].setRange(0, 15)
        self.chart.axes(Qt.Horizontal)[0].setGridLineVisible(True)

        self.chart.axes(Qt.Vertical)[0].setRange(0, 15)

class ChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)

        self.hLine = QGraphicsLineItem()
        self.vLine = QGraphicsLineItem()
        pen = QPen(Qt.red)
        self.hLine.setPen(pen)
        self.vLine.setPen(pen)
        self.scene().addItem(self.hLine)
        self.scene().addItem(self.vLine)

    def mouseMoveEvent(self, event: QMouseEvent):
        # # 마우스 포인터 위치에 따라 선과 툴팁 업데이트
        # # super().mouseMoveEvent(event)
        # pos = event.position()
        # x = self.chart.mapToValue(pos, self.series).x()
        # y = self.chart.mapToValue(pos, self.series).y()

        # print(x, y)
        # # 여기에 수평/수직 선을 업데이트하는 코드와 툴팁을 표시하는 코드를 추가
        #! ----------------------------- CrossHair ---------------------------- #
        # super().mouseMoveEvent(event)
        graphic_pos = self.mapToScene(event.pos()) #parent function execute
        chart_value = self.chart().mapToValue(event.pos())
        plotarea = self.chart().plotArea()
        # print("--------------------------------------------------")
        # print(f"graphic_pos {graphic_pos}")
        # print(f"chart_value {chart_value}")

        if plotarea.contains(graphic_pos):
            closest_x = round(chart_value.x())
            chart_value.setX(closest_x)
            # print(f"closest_x {closest_x}")
            # print(f"chart_value {chart_value}")

            # print(self.chart().mapToPosition(chart_value))
            graphic_pos = self.chart().mapToPosition(chart_value)
            self.hLine.setLine(plotarea.left(), graphic_pos.y(), plotarea.right(), graphic_pos.y())
            self.vLine.setLine(graphic_pos.x(), plotarea.top(), graphic_pos.x(), plotarea.bottom())

        #! ----------------------------- Tooltips ----------------------------- #
            tooltip_text = f"X: {chart_value.x():.2f}, Y: {chart_value.y():.2f}"
            QToolTip.showText(event.globalPos(), tooltip_text)
        #! -------------------------------------------------------------------- #
        # chart_pos_series = self.chart().mapToValue(pos, self.chart().series()[0])

        # x = chart_pos.x()
        # y = chart_pos.y()

        # 마우스 위치에 따른 수평 및 수직 선 업데이트
        # 여기에 수평/수직 선을 업데이트하는 코드와 툴팁을 표시하는 코드를 추가
        # print(f"X: {x}, Y: {y}")  # 콘솔에 출력 (툴팁 대신)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChartWindow()
    window.show()
    sys.exit(app.exec())
