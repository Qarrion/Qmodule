from PySide6 import QtWidgets
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent
import pyqtgraph as pg
import random, sys
import numpy as np
from PySide6.QtCore import QTimer

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=True, y=True) # 자동 range (add)
        self.setAutoVisible(x=False, y=True)  # 자동 min max

    def wheelEvent(self, event):
        # 확대/축소 비율 설정
        x_min, x_max = self.viewRange()[0]
        print(x_min, x_max)
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() > 0:
            # self.scaleBy((1/factor, 1))
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.x = np.array([])
        self.y = np.array([])
        self.plot_dataitem = self.plot(self.x,self.y,antialias=True)
        print(self.window)

    def update_dataitem(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
        self.plot_dataitem.setData(self.x, self.y)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pw = PlotWidget(viewBox=ViewBox())
        self.setCentralWidget(self.pw)

        # -------------------------------------------------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 
        self.pw.update_dataitem(x, y)
        # -------------------------------------------------------------------- #

        self.timer = QTimer()
        self.timer.setInterval(50)  # 500 밀리초마다 업데이트
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        x_new = len(self.pw.x)
        y_new = np.random.normal(size=1)[0] + 5 * np.sin(x_new/100) 
        self.pw.update_dataitem(x_new, y_new)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()