from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QCandlestickSeries, QCandlestickSet, QDateTimeAxis, QValueAxis,QBarCategoryAxis
from PySide6.QtCore import QDateTime, Qt
import sys
import random

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        # 차트 및 캔들스틱 시리즈 생성
        chart = QChart()
        series = QCandlestickSeries()
        series.setIncreasingColor(Qt.green)
        series.setDecreasingColor(Qt.red)

        
        axisX = QBarCategoryAxis()
        
        # 영업일 데이터 추가
        datetime = QDateTime.currentDateTime()
        dd=[]
        for _ in range(10):  # 임의의 10 영업일
            if datetime.date().dayOfWeek() <= 5:  # 주말이 아닐 때만 데이터 추가
                open_price = random.uniform(100, 200)
                close_price = random.uniform(100, 200)
                high_price = max(open_price, close_price) + random.uniform(0, 10)
                low_price = min(open_price, close_price) - random.uniform(0, 10)
                candlestick_set = QCandlestickSet(open_price, high_price, low_price, close_price, _)
                series.append(candlestick_set)
                time_labels = datetime.toString("MM-dd")
                # print(time_labels)
                dd.append(time_labels)
                # axisX.append(time_labels)

            datetime = datetime.addDays(1)

        axisX.append(dd)
        chart.addSeries(series)

        # X축 (QDateTimeAxis) 설정
        # axisX = QDateTimeAxis()
        # axisX.setFormat("dd MMM")  # 날짜 형식
        # axisX.setTitleText("Date")
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        # Y축 (QValueAxis) 설정
        axisY = QValueAxis()
        axisY.setTitleText("Price")
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        # 차트 뷰 생성 및 윈도우에 추가
        chartView = QChartView(chart)
        self.setCentralWidget(chartView)

# 애플리케이션 실행
app = QApplication(sys.argv)
win = MyWindow()
win.show()
sys.exit(app.exec())