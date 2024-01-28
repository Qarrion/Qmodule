from PySide6 import QtWidgets
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent
import pyqtgraph as pg
import random, sys
import numpy as np

# ---------------------------------- diagram --------------------------------- #
# https://pyqtgraph.readthedocs.io/en/latest/api_reference/uml_overview.html


# https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/graphicsItems/ViewBox/ViewBox.html
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(y=True)
        self.setAutoVisible(y=True)
        
    def wheelEvent(self, event):
        # 확대/축소 비율 설정
        x_min, x_max = self.viewRange()[0]
        print(x_min, x_max)
        x_rng = (x_max - x_min) * 0.1
        
        # print(event.delta().y())
        if event.delta() > 0:
            # self.scaleBy((1/factor, 1))
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

# https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/widgets/PlotWidget.html#PlotWidget
# https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotitem.html
class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # viewBox = ViewBox()
        
        # self.plotItem.setMouseEnabled(y=False)
        # -------------------------------------------------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 

        self.plot_data_item = self.plot(x,y,antialias=True)
        # -------------------------------------------------------------------- #
        # self.sigXRangeChanged.connect(self.update_y_range_given_x_range)
        
    # def update_y_range_given_x_range(self,  viewbox):
    #     # print(self.plot_data_item.getData())
    #     # print(viewbox.viewRange()[0])
    #     xdata = self.plot_data_item.getData()[0]
    #     ydata = self.plot_data_item.getData()[1]
    #     x_min, x_max = viewbox.viewRange()[0]
    #     y_given_x_range = ydata[(xdata >= x_min) & (xdata <= x_max)]

    #     viewbox.setYRange(min(y_given_x_range),max(y_given_x_range))



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # x = np.arange(1000, dtype=float)
        # y = np.random.normal(size=1000)
        # y += 5 * np.sin(x/100) 

        #! plot
        # -------------------------------------------------------------------- #
        # self.pw=pg.PlotWidget(viewBox = ViewBox())
        # self.pw.plot(x,y,antialias=True)
        self.pw = PlotWidget(viewBox=ViewBox())
        # -------------------------------------------------------------------- #

        self.setCentralWidget(self.pw)





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()