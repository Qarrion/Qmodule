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
        custom_ticks = [(1.5, 'CustomTick1.5')]
        
        y_axis = self.plot_item.getAxis('left')
        y_axis.setTicks([major_ticks, minor_ticks, custom_ticks])
        
        # 특정 레벨의 틱 스타일 설정

        # # 틱 레벨 스타일을 설정
        # tick_level = 2  # 변경하려는 틱 레벨
        # tick_style = {'color': 'red', 'background': 'yellow'}  # 원하는 색상 및 배경 색상 설정

        # # 틱 레벨에 대한 스타일을 설정하기 위해 튜플을 사용
        # y_axis.setStyle(tickStyle={tick_level: tick_style})
        custom_tick_level = y_axis._tickLevels[2]  # 세 번째 레벨의 틱 스타일 가져오기

        # custom_tick_level['font'] = pg.QtGui.QFont("Arial", 12)
        # custom_tick_level['offset'] = 15
        # custom_tick_level['color'] = (255, 0, 0)
        # custom_tick_level['background'] = (0, 255, 0)

        # 데이터 생성 및 플롯
        self.plot_data = np.array([1, 2, 3, 4, 5])
        self.plot_item.plot(self.plot_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
