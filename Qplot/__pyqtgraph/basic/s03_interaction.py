from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np

#$ ---------------------------------------------------------------------------- #
#$                                      fix                                     #
#$ ---------------------------------------------------------------------------- #
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super(ViewBox,self).__init__(*args, **kwargs)
        self.setMouseEnabled(y=False) # False
        self.enableAutoRange(x=False, y=False) #! 자동 range (add)
        self.setAutoVisible(x=False, y=False)  #! 자동 min max

    # ------------------------------ mouse wheel ----------------------------- #
    def wheelEvent(self, event):
        x_min, x_max = self.viewRange()[0]
        x_rng = (x_max - x_min) * 0.1
        if event.delta() > 0:
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

class AutoScale:
    def __init__(self, plotwidget:pg.PlotWidget):
        self.pw = plotwidget

    # -------------------------------- x range ------------------------------- #
    def x_minmax(self, x_data):
        x_sta = min(x_data)
        x_end = max(x_data) 
        self.pw.setXRange(x_sta, x_end, padding=0.05)
    
    def x_window(self, x_data):
        x_min, x_max = self.getViewBox().viewRange()[0]
        threshold = (x_max-x_min)*0.05 
        if x_max - threshold <= len(x_data) <= x_max + 1 :
            self.pw.setXRange(x_min + threshold, x_max + threshold, padding=0.00)

    # -------------------------------- y range ------------------------------- #
    def y_rangex(self, x_data, y_datas:list):
        x_min, x_max = self.pw.getViewBox().viewRange()[0]
        y_min, y_max = self.pw.getViewBox().viewRange()[1]

        x_mask = (x_data >= x_min) & (x_data <= x_max)
        if sum(x_mask) > 0:
            y_data_min = np.min([np.min(y_data) for y_data in y_datas])
            y_data_max = np.max([np.max(y_data) for y_data in y_datas])
            if not (y_data_min == y_min and y_data_max == y_max):
                self.pw.setYRange(y_data_min, y_data_max)

#% ---------------------------------------------------------------------------- #
#%                                    custom                                    #
#% ---------------------------------------------------------------------------- #
class CrossHair:
    def __init__(self, plotitem:pg.PlotItem):
        self.plotitem = plotitem

        self.pos_scene = QtCore.QPointF(0,0)

        self.vline = pg.InfiniteLine(angle=90, movable=False)
        self.hline = pg.InfiniteLine(angle=0, movable=False)
        # self.hline = pg.InfiniteLine(angle=0, movable=False,pos=0, label="aaa")

        self.plotitem.addItem(self.vline, ignoreBounds=False)
        self.plotitem.addItem(self.hline, ignoreBounds=False)

    def slot_mouse_moved(self, pos):
        self.pos_scene = pos
        self._update()

    def slot_range_changed(self):
        self._update()

    def _update(self):
        """initial"""
        mousePoint = self.plotitem.vb.mapSceneToView(self.pos_scene)
        self.vline.setPos(mousePoint.x())
        self.hline.setPos(mousePoint.y())

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showGrid(x=True,y=True)
        self.plotitem = self.getPlotItem()
        self.autoscale = AutoScale(self)
        self.crosshar = CrossHair(self.plotitem)
        
        #@ ------------------------------ signal ------------------------------ #
        self.scene().sigMouseMoved.connect(self.slot_mouse_moved)
        self.getViewBox().sigRangeChanged.connect(self.slot_range_changed)

        # ------------------------------- plot1 ------------------------------ #
        self.data_line_x = np.array([])
        self.data_line_y = np.array([])

        self.line = pg.PlotCurveItem(self.data_line_x,self.data_line_y,antialias=True)
        self.plotitem.addItem(self.line)
        # -------------------------------------------------------------------- #

    #@ -------------------------------- update -------------------------------- #
    def update_data(self, x , y, append=True):
        # ------------------------------- plot1 ------------------------------ #
        if append:
            self.data_line_x = np.append(self.data_line_x, x)
            self.data_line_y = np.append(self.data_line_y, y)
        else:
            self.data_line_x[-1] = x
            self.data_line_y[-1] = y

        self.line.setData(self.data_line_x, self.data_line_y)
        # ----------------------------- autoscale ---------------------------- #
        self.autoscale.x_minmax(self.data_line_x)
        self.autoscale.y_rangex(self.data_line_x, [self.data_line_y])

    #@ --------------------------------- slot --------------------------------- #
    def slot_mouse_moved(self, evt):
        self.crosshar.slot_mouse_moved(evt)

    def slot_range_changed(self):
        self.crosshar.slot_range_changed()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plotwidget = PlotWidget(viewBox=ViewBox())
        # ------------------------------- data ------------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 2000 * np.sin(x/100) 
        self.plotwidget.update_data(x,y) #!init
        self.plotwidget.crosshar._update()
        # -------------------------------------------------------------------- #    
        self.setCentralWidget(self.plotwidget)
        # print(self.plotwidget.autoscale.x_set)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


