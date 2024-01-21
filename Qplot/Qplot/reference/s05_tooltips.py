import sys
from PySide6.QtCharts import QChart, QChartView, QCandlestickSeries, QCandlestickSet
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtWidgets import QApplication, QToolTip

class CandlestickChartView(QChartView):
    def __init__(self, chart, series):
        super().__init__(chart)
        self.series = series

    def mouseMoveEvent(self, event: QMouseEvent):
        # 마우스 포인터 위치에서 차트의 좌표로 변환
        chart_pos = self.chart().mapToValue(event.pos())

        # 캔들스틱 시리즈의 각 세트를 확인하여 마우스 위치와 가까운지 확인
        for set in self.series.sets():
            if abs(set.timestamp() - chart_pos.x()) < 0.5:  # X축 기준으로 충분히 가까운 경우
                # 툴팁 표시
                tooltip_text = f"Open: {set.open()}\nHigh: {set.high()}\nLow: {set.low()}\nClose: {set.close()}"
                QToolTip.showText(event.globalPos(), tooltip_text)
                return
        QToolTip.hideText()
        super().mouseMoveEvent(event)

def create_candlestick_chart():
    # 캔들스틱 시리즈 생성 및 데이터 추가
    series = QCandlestickSeries()
    # (시리즈에 데이터 추가...)

    # 차트 생성 및 설정
    chart = QChart()
    chart.addSeries(series)
    chart.createDefaultAxes()

    # 차트 뷰 생성
    chart_view = CandlestickChartView(chart, series)
    chart_view.setRenderHint(QPainter.Antialiasing)
    return chart_view

# Qt 애플리케이션 실행
app = QApplication(sys.argv)
chart_view = create_candlestick_chart()
chart_view.show()
sys.exit(app.exec())