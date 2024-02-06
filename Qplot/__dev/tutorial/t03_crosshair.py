from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np



class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=False, y=False) #! 자동 range    autorange
        self.setAutoVisible(x=False, y=False)  #! 자동 min max  autorange
        # ['xMin', 'xMax', 'yMin', 'yMax', 'minXRange', 'maxXRange', 'minYRange', 'maxYRange']
        self.setLimits(minXRange=10) 

    def wheelEvent(self, event):
        x_min, x_max = self.viewRange()[0]
        x_rng = (x_max - x_min) * 0.1
        x_min_new = x_min - x_rng if event.delta() < 0 else x_min + x_rng
        self.setXRange(x_min_new , x_max, padding=0)

class  PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        # ------------------------------ viewbox ----------------------------- #
        self.viewbox = ViewBox()
        kwargs.update({'viewBox':self.viewbox})          #* plotItem(viewBox) *#
        super().__init__(*args, **kwargs)
        # ----------------------------- autorange ---------------------------- #
        self.autorng = AutoRange(self.viewbox)          
        # ----------------------------- crosshair ---------------------------- #
        self.crosshair = CrossHair(self.viewbox)
        # ----------------------------- plotItem ----------------------------- #
        self.plotItem.showGrid(x=True, y=True)
        # ------------------------------ signal ------------------------------ #
        self.scene().sigMouseMoved.connect(self.slot_mouse_moved)
        self.getViewBox().sigRangeChanged.connect(self.slot_range_changed)


        #@ ------------------------------- plot ------------------------------- #
        # -------------------------------------------------------------------- #
        self.data_line_x = np.array([])
        self.data_line_y = np.array([])
        self.plot_line =  pg.PlotCurveItem(
                                self.data_line_x,self.data_line_y,antialias=True)

        self.plotItem.addItem(self.plot_line)
        # -------------------------------------------------------------------- #

    def update_data(self, line_x, line_y, append=True):
        #@ ------------------------------ update ------------------------------ #
        if append:
            self.data_line_x = np.append(self.data_line_x, line_x)
            self.data_line_y = np.append(self.data_line_y, line_y)
        else:
            self.data_line_x[-1] = line_x
            self.data_line_y[-1] = line_y
        self.plot_line.setData(self.data_line_x,self.data_line_y)   #* setData *#

        self.autorng.x_minmax(x_data=self.data_line_x)            #% autorange %#
        self.autorng.y_givenx(x_data=self.data_line_x, y_datas=[self.data_line_y])

    def slot_mouse_moved(self, evt):
        # ---------------------------- slot_mouse ---------------------------- #
        self.crosshair.slot_mouse_moved(evt)                      #% crosshair %#

    def slot_range_changed(self):
        # ---------------------------- slot_range ---------------------------- #
        self.crosshair.slot_range_changed()                       #% crosshair %#
        self.autorng.y_givenx(x_data=self.data_line_x, y_datas=[self.data_line_y])
 
class CrossHair:
    def __init__(self, viewbox:pg.ViewBox):
        self.vb = viewbox
        self.data_scene_pos = pg.QtCore.QPointF(0,0)

        pen = pg.mkPen(color="#cccccc", style=pg.QtCore.Qt.DashLine, width=0.6)
        self.vline = pg.InfiniteLine(angle=90, movable=False,pen=pen)
        self.hline = pg.InfiniteLine(angle=0, movable=False,pen=pen)
        
        self.vb.addItem(self.vline, ignoreBounds=False)
        self.vb.addItem(self.hline, ignoreBounds=False)

    def slot_mouse_moved(self, pos):
        self.data_scene_pos = pos
        self.update_position()

    def slot_range_changed(self):
        self.update_position()

    def update_position(self):
        mousePoint = self.vb.mapSceneToView(self.data_scene_pos)
        self.vline.setPos(mousePoint.x()) ## round(mousePoint.x())
        self.hline.setPos(mousePoint.y()) ## round(mousePoint.x())

class AutoRange:
    def __init__(self, viewbox:pg.ViewBox):
        self.vb = viewbox

    def x_minmax(self, x_data):
        x_sta = min(x_data)
        x_end = max(x_data) 
        self.vb.setXRange(x_sta, x_end, padding=0.05)

    def x_window(self, x_data):
        x_min, x_max = self.vb.viewRange()[0]
        threshold = (x_max-x_min)*0.05 
        if x_max - threshold <= len(x_data) <= x_max + 1 :
            self.vb.setXRange(x_min + threshold, x_max + threshold, padding=0.00)

    def y_givenx(self, x_data, y_datas:list):
        x_min, x_max = self.vb.getViewBox().viewRange()[0]
        y_min, y_max = self.vb.getViewBox().viewRange()[1]
        x_mask = (x_data >= x_min) & (x_data <= x_max)
        if sum(x_mask) > 0:
            y_data_min = np.min([np.min(y_data[x_mask]) for y_data in y_datas])
            y_data_max = np.max([np.max(y_data[x_mask]) for y_data in y_datas])
            if not (y_data_min == y_min and y_data_max == y_max):
                print(y_data_min, y_data_max)
                self.vb.setYRange(y_data_min, y_data_max)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pwg = PlotWidget()

        # ----------------------------- init data ---------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 
        pwg.update_data(x,y)
        # -------------------------------------------------------------------- #
        self.setCentralWidget(pwg)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MainWindow()

    win.show()
    app.exec()