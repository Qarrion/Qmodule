import sys
from PySide6.QtWidgets import QApplication,QLabel,QMainWindow
import pyqtgraph as pg
import numpy as np

class CustomPlot(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotitem = self.getPlotItem()
        self.plotitem.showGrid(x=True, y=True)
        self.setMouseTracking(True)  # 마우스 추적 활성화

    def mouseMoveEvent(self, event):
        mousePoint = self.plotitem.vb.mapSceneToView(event.position())
        y_value = mousePoint.y()
        # self.tickviewer.setTickValue()

class CViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super(CViewBox,self).__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        # self.enableAutoRange(x=False, y=False) # 자동 range (add)
        # self.setAutoVisible(x=False, y=False)  # 자동 min max
        
    def wheelEvent(self, event):
        x_min, x_max = self.viewRange()[0]
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() < 0:
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

app = QApplication([])
# ---------------------------------- window ---------------------------------- #
window = QMainWindow()
# --------------------------------- gen plot --------------------------------- #
x = np.arange(1000, dtype=float)
y = np.random.normal(size=1000)
y += 5 * np.sin(x/100) 
# ---------------------------------------------------------------------------- #

plot_widget =  pg.PlotWidget(viewBox=CViewBox())
plot_item = plot_widget.getPlotItem()

data_item = pg.PlotCurveItem(x,y,antialias=True)

plot_item.addItem(data_item)
# ---------------------------------------------------------------------------- #
plot_item.showAxis('right')


# ---------------------------------------------------------------------------- #

# --------------------------------- add plot --------------------------------- #
window.setCentralWidget(plot_widget)
window.show()

app.exec()
