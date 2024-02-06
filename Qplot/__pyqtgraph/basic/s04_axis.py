from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np

# #$ ---------------------------------------------------------------------------- #
# #$                                      fix                                     #
# #$ ---------------------------------------------------------------------------- #
# class ViewBox(pg.ViewBox):
#     def __init__(self, *args, **kwargs):
#         super(ViewBox,self).__init__(*args, **kwargs)
#         self.setMouseEnabled(y=False) # False
#         self.enableAutoRange(x=False, y=False) #! 자동 range (add)
#         self.setAutoVisible(x=False, y=False)  #! 자동 min max

#     # ------------------------------ mouse wheel ----------------------------- #
#     def wheelEvent(self, event):
#         x_min, x_max = self.viewRange()[0]
#         x_rng = (x_max - x_min) * 0.1
#         if event.delta() > 0:
#             self.setXRange(x_min - x_rng , x_max, padding=0)
#         else:
#             self.setXRange(x_min + x_rng , x_max, padding=0)

# class AutoScale:
#     def __init__(self, plotwidget:pg.PlotWidget):
#         self.pw = plotwidget

#     # -------------------------------- x range ------------------------------- #
#     def x_minmax(self, x_data):
#         x_sta = min(x_data)
#         x_end = max(x_data) 
#         self.pw.setXRange(x_sta, x_end, padding=0.05)
    
#     def x_window(self, x_data):
#         x_min, x_max = self.getViewBox().viewRange()[0]
#         threshold = (x_max-x_min)*0.05 
#         if x_max - threshold <= len(x_data) <= x_max + 1 :
#             self.pw.setXRange(x_min + threshold, x_max + threshold, padding=0.00)

#     # -------------------------------- y range ------------------------------- #
#     def y_rangex(self, x_data, y_datas:list):
#         x_min, x_max = self.pw.getViewBox().viewRange()[0]
#         y_min, y_max = self.pw.getViewBox().viewRange()[1]

#         x_mask = (x_data >= x_min) & (x_data <= x_max)
#         if sum(x_mask) > 0:
#             y_data_min = np.min([np.min(y_data) for y_data in y_datas])
#             y_data_max = np.max([np.max(y_data) for y_data in y_datas])
#             if not (y_data_min == y_min and y_data_max == y_max):
#                 self.pw.setYRange(y_data_min, y_data_max)

# #% ---------------------------------------------------------------------------- #
# #%                                    custom                                    #
# #% ---------------------------------------------------------------------------- #
# class CrossHair:
#     def __init__(self, plotitem:pg.PlotItem):
#         self.plotitem = plotitem

#         self.pos_scene = QtCore.QPointF(0,0)

#         pen = pg.mkPen(color="#cccccc", style=QtCore.Qt.DashLine, width=0.6)
#         self.vline = pg.InfiniteLine(angle=90, movable=False,pen=pen )
#         self.hline = pg.InfiniteLine(angle=0, movable=False,pen=pen)

#         self.plotitem.addItem(self.vline)
#         self.plotitem.addItem(self.hline)

#     def slot_mouse_moved(self, pos):
#         self.pos_scene = pos
#         self._update()

#     def slot_range_changed(self):
#         self._update()

#     def _update(self):
#         """initial"""
#         mousePoint = self.plotitem.vb.mapSceneToView(self.pos_scene)
#         self.vline.setPos(mousePoint.x())
#         self.hline.setPos(mousePoint.y())

# class PlotWidget(pg.PlotWidget):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.showGrid(x=True,y=True)
#         self.plotitem = self.getPlotItem()
#         self.plotItem.showAxis('right')
#         self.autoscale = AutoScale(self)
#         self.crosshair = CrossHair(self.plotitem)
        
#         #@ ------------------------------ signal ------------------------------ #
#         self.scene().sigMouseMoved.connect(self.slot_mouse_moved)
#         self.getViewBox().sigRangeChanged.connect(self.slot_range_changed)

#         # ------------------------------- plot1 ------------------------------ #
#         self.data_line_x = np.array([])
#         self.data_line_y = np.array([])

#         self.line = pg.PlotCurveItem(self.data_line_x,self.data_line_y,antialias=True)
#         self.plotitem.addItem(self.line)
#         # -------------------------------------------------------------------- #

#     #@ -------------------------------- update -------------------------------- #
#     def update_data(self, x , y, append=True):
#         # ------------------------------- plot1 ------------------------------ #
#         if append:
#             self.data_line_x = np.append(self.data_line_x, x)
#             self.data_line_y = np.append(self.data_line_y, y)
#         else:
#             self.data_line_x[-1] = x
#             self.data_line_y[-1] = y

#         self.line.setData(self.data_line_x, self.data_line_y)
#         # ----------------------------- autoscale ---------------------------- #
#         self.autoscale.x_minmax(self.data_line_x)
#         self.autoscale.y_rangex(self.data_line_x, [self.data_line_y])

#     #@ --------------------------------- slot --------------------------------- #
#     def slot_mouse_moved(self, evt):
#         self.crosshair.slot_mouse_moved(evt)

#     def slot_range_changed(self):
#         self.crosshair.slot_range_changed()

# #? ---------------------------------------------------------------------------- #
# from datetime import datetime, timedelta

# def wdays(start_date, num_days):
#     business_days = []
#     current_date = start_date
#     while len(business_days) < num_days:
#         # 주말이 아닌 경우에만 추가 (주말: 5 = 토요일, 6 = 일요일)
#         if current_date.weekday() < 5:
#             business_days.append(current_date)
#         # 다음 날짜로 이동
#         current_date += timedelta(days=1)

#     return business_days
# #? ---------------------------------------------------------------------------- #

# class DateAxis(pg.AxisItem):
#     def __init__(self, dates, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.dates = dates

#     def tickStrings(self, values, scale, spacing):
#         print(values)
#         return [self.dates[int(value)].strftime('%Y-%m-%d') if 0 <= int(value) < len(self.dates) else '' for value in values]

# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         # ------------------------------- data ------------------------------- #
#         n=10
#         x = np.arange(n)
#         y = np.array([0 if i % 2 == 0 else i for i in range(n)])
#         d = wdays(datetime(2023,1,24), n+1)
#         # print(d)
#         # -------------------------------------------------------------------- #
#         self.axis_x = DateAxis(d, 'bottom')
#         self.plotwidget = PlotWidget(viewBox=ViewBox(),axisItems={'bottom': self.axis_x})
#         self.plotwidget.update_data(x,y) #!init
#         self.plotwidget.crosshair._update()
#         # -------------------------------------------------------------------- #    
#         self.setCentralWidget(self.plotwidget)
#         # print(self.plotwidget.autoscale.x_set)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec()
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #

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

        pen = pg.mkPen(color="#cccccc", style=QtCore.Qt.DashLine, width=0.6)
        self.vline = pg.InfiniteLine(angle=90, movable=False,pen=pen, label="x={value}" ,bounds = [-20, 20])
        self.hline = pg.InfiniteLine(angle=0, movable=False,pen=pen)

        self.plotitem.addItem(self.vline)
        self.plotitem.addItem(self.hline)

    def slot_mouse_moved(self, pos):
        self.pos_scene = pos
        self._update()

    def slot_range_changed(self):
        self._update()

    def _update(self):
        """initial"""
        mousePoint = self.plotitem.vb.mapSceneToView(self.pos_scene)
        self.vline.setPos(round(mousePoint.x()))
        self.hline.setPos(mousePoint.y())
        # self.vline.label.setText(f"X={mousePoint.x()}")

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showGrid(x=True,y=True)
        self.plotitem = self.getPlotItem()
        self.plotitem.showAxis('right')

        self.autoscale = AutoScale(self)
        self.crosshair = CrossHair(self.plotitem)

        # ------------------------------- axis ------------------------------- #
        self.axis_bottom = DateAxis(orientation='bottom')
        self.plotitem.setAxisItems({'bottom':self.axis_bottom})

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
    def update_data(self, x , y, d, append=True):
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
        # ---------------------------- axis_bottom --------------------------- #
        self.axis_bottom.set_dates(d, append)

    #@ --------------------------------- slot --------------------------------- #
    def slot_mouse_moved(self, evt):
        self.crosshair.slot_mouse_moved(evt)

    def slot_range_changed(self):
        self.crosshair.slot_range_changed()

#? ---------------------------------------------------------------------------- #
from datetime import datetime, timedelta

def wdays(start_date, num_days):
    business_days = []
    current_date = start_date
    while len(business_days) < num_days:
        # 주말이 아닌 경우에만 추가 (주말: 5 = 토요일, 6 = 일요일)
        if current_date.weekday() < 5:
            business_days.append(current_date)
        # 다음 날짜로 이동
        current_date += timedelta(days=1)

    return business_days
#? ---------------------------------------------------------------------------- #

class DateAxis(pg.AxisItem):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.dates = np.array([])

    def set_dates(self, dates, append=True):
        if append:
            self.dates = np.append(self.dates, dates)
        else:
            self.dates[-1] = dates
        # self.dates = dates
        # print("set",self.dates)

    def tickStrings(self, values, scale, spacing):
        # print("tick",self.dates)
        return [self.dates[int(value)].strftime('%Y-%m-%d') if 0 <= int(value) < len(self.dates) else '' for value in values]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # ------------------------------- data ------------------------------- #
        n=10
        x = np.arange(n)
        y = np.array([0 if i % 2 == 0 else i for i in range(n)])
        d = wdays(datetime(2023,1,24), n+1)
        # print(d)

        # -------------------------------------------------------------------- #
        # self.axis_x = DateAxis('bottom')
        # self.plotwidget = PlotWidget(viewBox=ViewBox(),axisItems={'bottom': self.axis_x})
        self.plotwidget = PlotWidget(viewBox=ViewBox())
        self.plotwidget.update_data(x,y,d) #!init
        self.plotwidget.crosshair._update()
        # -------------------------------------------------------------------- #    
        self.setCentralWidget(self.plotwidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()