from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enableAutoRange()
        self.setMouseEnabled()
        self.setAutoVisible()   

class  PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        self.viewbox = ViewBox()
        kwargs.update({'viewBox':self.viewbox})  # plotItem(viewBox)
        super().__init__(*args, **kwargs)

        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 

        self.lineitem = pg.PlotCurveItem(x,y,antialias=True)
        self.plotItem.addItem(self.lineitem)
        # self.plotItem.showAxis('right')

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()

    pwg = PlotWidget()

    win.setCentralWidget(pwg)
    win.show()
    app.exec()