import sys
from PySide6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 데이터 준비
        x = np.array([0, 1, 2, 3])  # x 값 (정수)
        y = np.array([1.2, 2.3, 3.4, 4.5])  # y 값 (소수)
        d = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]  # d 값 (날짜)

        # PlotWidget 생성
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # 라인 차트 그리기
        self.graphWidget.plot(x, y, pen=pg.mkPen(color=(255, 0, 0), width=2))

        # x축 레이블 설정
        axis = self.graphWidget.getAxis('bottom')
        axis.setTicks([[(i, d[i]) for i in x]])  # x 위치에 날짜 레이블 설정
        print([[(i, d[i]) for i in x]])
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

import datetime


class CustomDateAxis(pg.DateAxisItem):
    def tickStrings(self, values, scale, spacing):
        # 타임스탬프를 날짜 포맷으로 변환
        strings = []
        for value in values:
            dt = datetime.datetime.fromtimestamp(value)
            if dt.day == 1:
                # 월의 첫 번째 날에는 월 이름을 전체로 표시
                strings.append(dt.strftime('%b'))  # 예: 'Jan', 'Feb', ...
            else:
                # 그 외에는 월의 일자만 표시
                strings.append(dt.strftime('%d'))  # 예: '01', '02', ...
        return strings