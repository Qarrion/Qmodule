import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QCandlestickSeries
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

class CandlestickChartExample(QMainWindow):
    def __init__(self):
        super().__init__()

        # 캔들스틱 시리즈 생성
        series = QCandlestickSeries()
        series.setDecreasingColor(Qt.red)
        series.setIncreasingColor(Qt.green)

        # 모델 생성 및 데이터 추가
        model = QStandardItemModel(4, 5)
        model.setHorizontalHeaderLabels(["Open", "High", "Low", "Close", "Timestamp"])
        self.populateModel(model)

        # 모델 및 매퍼 설정
        series.setModel(model)
        series.setOpenColumn(0)
        series.setHighColumn(1)
        series.setLowColumn(2)
        series.setCloseColumn(3)
        series.setTimestampColumn(4)

        # 차트 생성 및 설정
        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart_view = QChartView(chart)
        self.setCentralWidget(chart_view)

    def populateModel(self, model):
        # 샘플 데이터 추가
        items = [
            [10, 15, 7, 12, 1],
            [11, 16, 9, 14, 2],
            [15, 19, 14, 17, 3],
            [13, 14, 11, 12, 4]
        ]
        for row, data in enumerate(items):
            for column, value in enumerate(data):
                item = QStandardItem(value)
                model.setItem(row, column, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CandlestickChartExample()
    window.show()
    sys.exit(app.exec())