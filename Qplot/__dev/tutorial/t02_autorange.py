from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np



class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=False, y=False) #! 자동 range (add)
        self.setAutoVisible(x=False, y=False)  #! 자동 min max 
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
        kwargs.update({'viewBox':self.viewbox})         #* plotItem(viewBox) *#
        super().__init__(*args, **kwargs)
        # ----------------------------- autorange ---------------------------- #
        self.autorng = AutoRange(self.viewbox)          
        # ----------------------------- plotItem ----------------------------- #
        self.plotItem.showGrid(x=True, y=True)
        
        #@ ------------------------------- plot ------------------------------- #
        self.data_line_x = np.array([])
        self.data_line_y = np.array([])
        self.plot_line =  pg.PlotCurveItem(
                                self.data_line_x,self.data_line_y,antialias=True)

        self.plotItem.addItem(self.plot_line)

    #! Custom
    def update_data(self, line_x, line_y, append=True):
        #@ ------------------------------ update ------------------------------ #
        if append:
            self.data_line_x = np.append(self.data_line_x, line_x)
            self.data_line_y = np.append(self.data_line_y, line_y)
        else:
            self.data_line_x[-1] = line_x
            self.data_line_y[-1] = line_y
        self.plot_line.setData(self.data_line_x,self.data_line_y) #* setData *#

        self.autorng.x_minmax(x_data=self.data_line_x)
        self.autorng.y_givenx(x_data=self.data_line_x, y_datas=[self.data_line_y])

class AutoRange: #! Range !#
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
