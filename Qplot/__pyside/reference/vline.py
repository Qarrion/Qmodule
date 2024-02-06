import sys
from PySide6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # PlotWidget 생성
        self.plotWidget = pg.PlotWidget()
        self.setCentralWidget(self.plotWidget)

        # 여러 세로선 데이터 생성
        x_positions = [1, 2, 3, 4, 5]  # X 좌표 위치
        y_min = 0  # Y 최소값
        y_max = 10  # Y 최대값

        # 각 세로선에 대한 데이터 생성 및 그리기
        for x in x_positions:
            x_values = [x, x]
            y_values = [y_min, y_max]
            self.plotWidget.plot(x_values, y_values, pen=pg.mkPen('b', width=2))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())