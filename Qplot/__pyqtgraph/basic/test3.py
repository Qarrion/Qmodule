import sys
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('PyQtGraph Example')

        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        self.plot_item = self.plot_widget.plotItem

        # 주요 틱 설정
        major_ticks = [(1, 'Tick1'), (3, 'Tick3'), (5, 'Tick5')]

        # 보조 틱 설정
        minor_ticks = [(2, 'MinorTick2'), (4, 'MinorTick4')]

        # 사용자 정의 틱 설정 (세 번째 레벨)
        custom_ticks = [(1.5, 'CustomTick1.5', {'color': (255, 0, 0), 'background': (0, 255, 0)})]

        y_axis = self.plot_item.getAxis('left')
        y_axis.setTicks([major_ticks, minor_ticks, custom_ticks])

        # 데이터 생성 및 플롯
        self.plot_data = np.array([1, 2, 3, 4, 5])
        self.plot_item.plot(self.plot_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
