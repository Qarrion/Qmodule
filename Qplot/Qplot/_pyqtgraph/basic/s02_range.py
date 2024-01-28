from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent


#! ---------------------------------------------------------------------------- #
#!                                     case4                                    #
#! ---------------------------------------------------------------------------- #

# app = QtWidgets.QApplication([])
# # ---------------------------------- window ---------------------------------- #
# window = QtWidgets.QMainWindow()
# # --------------------------------- gen plot --------------------------------- #
# x = np.arange(1000, dtype=float)
# y = np.random.normal(size=1000)
# y += 5 * np.sin(x/100) 
# # ---------------------------------------------------------------------------- #

# plot_widget = pg.PlotWidget()
# view_box = plot_widget.getViewBox()
# view_box.setMouseEnabled(y=False)
# view_box.enableAutoRange(y=True)
# view_box.setAutoVisible(y=True)
# plot_item = plot_widget.getPlotItem()

# data_item = pg.PlotCurveItem(x,y,antialias=True)

# plot_item.addItem(data_item)
# # --------------------------------- add plot --------------------------------- #
# window.setCentralWidget(plot_widget)
# window.show()

# app.exec()

#! ---------------------------------------------------------------------------- #
#!                                     case5                                    #
#! ---------------------------------------------------------------------------- #

# class ViewBox(pg.ViewBox):
#     def __init__(self, *args, **kwargs):
#         super(ViewBox,self).__init__(*args, **kwargs)
#         self.setMouseEnabled(y=False)
#         self.enableAutoRange(x=True, y=True) # 자동 range (add)
#         self.setAutoVisible(x=False, y=True)  # 자동 min max

#     def wheelEvent(self, event):
#         x_min, x_max = self.viewRange()[0]
#         print(x_min, x_max)
#         x_rng = (x_max - x_min) * 0.1
        
#         if event.delta() > 0:
#             self.setXRange(x_min - x_rng , x_max, padding=0)
#         else:
#             self.setXRange(x_min + x_rng , x_max, padding=0)

# class PlotWidget(pg.PlotWidget):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         x = np.arange(1000, dtype=float)
#         y = np.random.normal(size=1000)
#         y += 5 * np.sin(x/100) 

#         self.plotitem = self.getPlotItem()
#         self.line = pg.PlotCurveItem(x,y,antialias=True)
#         self.plotitem.addItem(self.line)

# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.plotwidget = PlotWidget(viewBox=ViewBox())
#         self.setCentralWidget(self.plotwidget)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec()

#! ---------------------------------------------------------------------------- #
#!                                     case6                                    #
#! ---------------------------------------------------------------------------- #

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super(ViewBox,self).__init__(*args, **kwargs)
        self.setMouseEnabled(y=False) # False
        self.enableAutoRange(x=False, y=False) #! 자동 range (add)
        self.setAutoVisible(x=False, y=False)  #! 자동 min max

    def wheelEvent(self, event):
        x_min, x_max = self.viewRange()[0]
        # print(x_min, x_max)
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() > 0:
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

class AutoScale:
    def __init__(self, plotwidget:pg.PlotWidget):
        self.pw = plotwidget

    #! -------------------------------- x range ------------------------------- #
    def x_minmax(self, x_data):
        x_sta = min(x_data)
        x_end = max(x_data) 
        self.pw.setXRange(x_sta, x_end, padding=0.05)
    
    def x_window(self, x_data):
        x_min, x_max = self.getViewBox().viewRange()[0]
        threshold = (x_max-x_min)*0.05 
        if x_max - threshold <= len(x_data) <= x_max + 1 :
            self.pw.setXRange(x_min + threshold, x_max + threshold, padding=0.00)

    def y_rangex(self, x_data, y_datas:list):
        x_min, x_max = self.pw.getViewBox().viewRange()[0]
        y_min, y_max = self.pw.getViewBox().viewRange()[1]

        x_mask = (x_data >= x_min) & (x_data <= x_max)
        if sum(x_mask) > 0:
            y_data_min = np.min([np.min(y_data) for y_data in y_datas])
            y_data_max = np.max([np.max(y_data) for y_data in y_datas])
            print(y_data_min, y_data_max)
            if not (y_data_min == y_min and y_data_max == y_max):
                self.pw.setYRange(y_data_min, y_data_max)

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoscale= AutoScale(self)
        # ------------------------------- plot1 ------------------------------ #
        self.line_x = np.array([])
        self.line_y = np.array([])

        self.plotitem = self.getPlotItem()
        self.line = pg.PlotCurveItem(self.line_x,self.line_y,antialias=True)
        self.plotitem.addItem(self.line)

        # -------------------------------------------------------------------- #

    #! ------------------------------ update data ----------------------------- #
    def update_data(self, x , y, append=True):
        if append:
            self.line_x = np.append(self.line_x, x)
            self.line_y = np.append(self.line_y, y)
        else:
            self.line_x[-1] = x
            self.line_y[-1] = y

        self.line.setData(self.line_x, self.line_y)
        #@ ----------------------------- autoscale ---------------------------- #
        self.autoscale.x_minmax(self.line_x)
        self.autoscale.y_rangex(self.line_x, [self.line_y])

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plotwidget = PlotWidget(viewBox=ViewBox())
        # ------------------------------- data ------------------------------- #
        x = np.arange(5, dtype=float)
        y = np.random.normal(size=5)
        y += 5 * np.sin(x/100) 
        self.plotwidget.update_data(x,y)
        # -------------------------------------------------------------------- #    
        self.setCentralWidget(self.plotwidget)
        # print(self.plotwidget.autoscale.x_set)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()









#! ---------------------------------------------------------------------------- #
#!                                     case4                                    #
#! ---------------------------------------------------------------------------- #

# class ViewBox2(pg.ViewBox):
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)
#         # self.enableAutoRange()
#         self.setMouseEnabled(y=False)
#         # self.enableAutoRange(x=True, y=False) # 자동 range (add)
#         # self.setAutoVisible(x=True, y=False)  # 자동 min max


#     def wheelEvent(self, event:QWheelEvent):
#         x_min, x_max = self.viewRange()[0]
#         x_rng = (x_max - x_min) * 0.1
#         print(x_rng)
#         if event.delta() < 0:
#             self.setXRange(x_min - x_rng , x_max, padding=0)
#         else:
#             self.setXRange(x_min + x_rng , x_max, padding=0)

# class PlotWidget(pg.PlotWidget):
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)
#         x = np.arange(1000, dtype=float)
#         y = np.random.normal(size=1000)
#         y += 5 * np.sin(x/100) 

#         viewbox = ViewBox2()
#         # plot_widget = pg.PlotWidget()
#         self.plot_item = self.getPlotItem()

#         self.data_item = pg.PlotCurveItem(x,y,antialias=True)

#         self.plot_item.addItem(self.data_item)
#         self.plot_item.vb = viewbox
# # --------------------------------- add plot --------------------------------- #



# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = QtWidgets.QMainWindow()

#     plot_widget = PlotWidget()

#     window.setCentralWidget(plot_widget)
#     window.show()
#     app.exec()



#! ---------------------------------------------------------------------------- #
#!                                     case5                                    #
#! ---------------------------------------------------------------------------- #


# class ViewBox(pg.ViewBox):
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)
#         # self.enableAutoRange()
#         self.setMouseEnabled(y=False)
#         # self.enableAutoRange(x=True, y=False) # 자동 range (add)
#         # self.setAutoVisible(x=True, y=False)  # 자동 min max

#     def wheelEvent(self, event):
#         x_min, x_max = self.viewRange()[0]
#         x_rng = (x_max - x_min) * 0.1
#         print(x_rng)
#         if event.delta() < 0:
#             self.setXRange(x_min - x_rng , x_max, padding=0)
#         else:
#             self.setXRange(x_min + x_rng , x_max, padding=0)

# class PlotWidget(pg.PlotWidget):
#     def __init__(self, *args, **kwds):
#         super().__init__(*args, **kwds)

#         x = np.arange(1000, dtype=float)
#         y = np.random.normal(size=1000)
#         y += 5 * np.sin(x/100) 

#         # plot_widget = pg.PlotWidget()
#         self.plot_item = self.getPlotItem()
#         self.data_item = pg.PlotCurveItem(x,y,antialias=True)
#         self.plot_item.addItem(self.data_item)

# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.plot_widget = PlotWidget(viewBox=ViewBox())
#         self.setCentralWidget(self.plot_widget)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec()