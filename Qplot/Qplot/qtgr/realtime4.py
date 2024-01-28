from PySide6 import QtWidgets
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent
from PySide6.QtCore import QPointF
import pyqtgraph as pg
import random, sys
import numpy as np
from PySide6.QtCore import QTimer

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=False, y=False) # 자동 range (add)
        self.setAutoVisible(x=False, y=False)  # 자동 min max
        

    def wheelEvent(self, event):
        # 확대/축소 비율 설정
        x_min, x_max = self.viewRange()[0]
        # print(x_min, x_max)
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
        
        self.showGrid(x=True,y=True)

        # -------------------------------------------------------------------- #
        self.last_pos = QPointF(0,0)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)  
        self.scene().sigMouseMoved.connect(self.mouseMoved)
        self.getViewBox().sigRangeChanged.connect(self.rangeChanged)
        # -------------------------------------------------------------------- #

    def update_dataitem(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
        self.plot_dataitem.setData(self.x, self.y)
        # self._update_xrange_window()
        # self._update_yrange_given_xrange()

    def amend_dataitem(self, x, y):
        self.x[-1] = x
        self.y[-1] = y
        self.plot_dataitem.setData(self.x, self.y)

    def update_yrange_given_xrange(self):
        x_min, x_max = self.getViewBox().viewRange()[0]
        y_min, y_max = self.getViewBox().viewRange()[1]

        xdata = self.plot_dataitem.getData()[0]
        ydata = self.plot_dataitem.getData()[1]

        ydata_given_xrange = ydata[(xdata >= x_min) & (xdata <= x_max)]
        if len(ydata_given_xrange)>0:
            y_min_new = min(ydata_given_xrange)
            y_max_new = max(ydata_given_xrange)
            if not (y_min_new == y_min and y_max_new == y_max):
                self.setYRange(y_min_new, y_max_new)
                
    def update_xrange_minmax(self, x_min=None, x_max=None):
        xdata = self.plot_dataitem.getData()[0]
        x_sta = min(xdata) if x_min is None else x_min
        x_end = max(xdata) if x_max is None else x_max
        self.setXRange(x_sta, x_end, padding=0.05)
        
    def update_xrange_window(self):
        x_min, x_max = self.getViewBox().viewRange()[0]
        xdata = self.plot_dataitem.getData()[0]
        threshold = (x_max-x_min)*0.05 
        
        if x_max - threshold <= len(xdata) <= x_max + 1 :
            self.setXRange(x_min + threshold, x_max + threshold, padding=0)

    def update_crosshair(self):
        mousePoint = self.plotItem.vb.mapSceneToView(self.last_pos)
        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

    # ------------------------------- callback ------------------------------- #
    def mouseMoved(self, evt):
        # 현재 마우스 위치 업데이트
        self.last_pos = evt 
        self.update_crosshair()

    def rangeChanged(self):
        self.update_crosshair()

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
        self.pw.update_xrange_minmax()
        self.pw.update_yrange_given_xrange()
        # -------------------------------------------------------------------- #

        self.timer = QTimer()
        self.timer.setInterval(50)  # 500 밀리초마다 업데이트
        self.timer.timeout.connect(self.update)
        self.timer.start()

        self.test_cnt = 0
    def update(self):
        x_new = len(self.pw.x)
        y_new = np.random.normal(size=1)[0] + 5 * np.sin(x_new/100) 

        #@ test---------------------------
        # if 
        
        
        #@ test---------------------------
        self.pw.update_dataitem(x_new, y_new)
        self.pw.update_xrange_window()
        self.pw.update_yrange_given_xrange()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()