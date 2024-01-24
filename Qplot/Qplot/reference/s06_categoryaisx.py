from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCharts import QChart, QChartView, QCandlestickSeries, QCandlestickSet, QDateTimeAxis, QValueAxis,  QCategoryAxis
from PySide6.QtCore import Qt, QDateTime
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



        axisX = QCategoryAxis() 

        # 영업일 데이터 추가 (주말은 무시)
        category_index = 0
        datetime = QDateTime.currentDateTime()
        for _ in range(30):  # 30일간의 데이터
            # 주말(토요일: 6, 일요일: 7)인 경우 다음 월요일로 이동
            if datetime.date().dayOfWeek() >= 6:
                days_until_monday = 8 - datetime.date().dayOfWeek()
                datetime = datetime.addDays(days_until_monday)
            
            open_price = random.uniform(100, 200)
            close_price = random.uniform(100, 200)
            high_price = max(open_price, close_price) + random.uniform(0, 10)
            low_price = min(open_price, close_price) - random.uniform(0, 10)
            candlestick_set = QCandlestickSet(open_price, high_price, low_price, close_price, category_index)
            series.append(candlestick_set)
            axisX.append(f"{datetime.date().toString('yyyy-MM-dd')}",category_index)

            datetime = datetime.addDays(1)

        chart.addSeries(series)

        # X축 (QDateTimeAxis) 설정
        
        # axisX.setLabelFormat("hh mm ss")  # 날짜 형식
        # axisX.setLabelFormat("yyyy-MM-dd")  # 날짜 형식
        axisX.setTitleText("Date")
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
