from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
import pyqtgraph as pg
import numpy as np

# ---------------------------------------------------------------------------- #
#                                     case1                                    #
# ---------------------------------------------------------------------------- #
# # ------------------------------------ app ----------------------------------- #
# app = QtWidgets.QApplication([])
# # ---------------------------------- window ---------------------------------- #
# window = QtWidgets.QMainWindow()

# # --------------------------------- gen plot --------------------------------- #
# x = np.arange(1000, dtype=float)
# y = np.random.normal(size=1000)
# y += 5 * np.sin(x/100) 

# pw = pg.PlotWidget()
# pw.plot(x,y)

# # --------------------------------- add plot --------------------------------- #
# window.setCentralWidget(pw)
# window.show()

# app.exec()



# ---------------------------------------------------------------------------- #
#                                     case2                                    #
# ---------------------------------------------------------------------------- #
# ------------------------------------ app ----------------------------------- #
# app = QtWidgets.QApplication([])
# # ---------------------------------- window ---------------------------------- #
# window = QtWidgets.QMainWindow()
# # --------------------------------- gen plot --------------------------------- #
# x = np.arange(1000, dtype=float)
# y = np.random.normal(size=1000)
# y += 5 * np.sin(x/100) 
# # ---------------------------------------------------------------------------- #
# plot_widget = pg.PlotWidget()


# data_item = pg.PlotDataItem(x,y)
# plot_widget.addItem(data_item)
# # --------------------------------- add plot --------------------------------- #
# window.setCentralWidget(plot_widget)
# window.show()
# app.exec()

#! ---------------------------------------------------------------------------- #
#!                                     case3                                    #
#! ---------------------------------------------------------------------------- #
# class ViewBox(pg.ViewBox):
#     def __init__(self, *args, **kwds):
#         super(ViewBox,self).__init__(*args, **kwds)
#         # self.enableAutoRange()
#         self.setMouseEnabled(y=False)
#         # self.enableAutoRange(x=False, y=False) # 자동 range (add)
#         # self.setAutoVisible(x=False, y=False)  # 자동 min max
        
#     def wheelEvent(self, event):
#         x_min, x_max = self.viewRange()[0]
#         x_rng = (x_max - x_min) * 0.1
        
#         if event.delta() < 0:
#             self.setXRange(x_min - x_rng , x_max, padding=0)
#         else:
#             self.setXRange(x_min + x_rng , x_max, padding=0)


# app = QtWidgets.QApplication([])
# # ---------------------------------- window ---------------------------------- #
# window = QtWidgets.QMainWindow()
# # --------------------------------- gen plot --------------------------------- #
# x = np.arange(1000, dtype=float)
# y = np.random.normal(size=1000)
# y += 5 * np.sin(x/100) 
# # ---------------------------------------------------------------------------- #

# plot_widget =  pg.PlotWidget(viewBox=ViewBox())
# plot_item = plot_widget.getPlotItem()



# data_item = pg.PlotCurveItem(x,y,antialias=True)

# plot_item.addItem(data_item)
# # ---------------------------------------------------------------------------- #
# plot_item.showAxis('right')


# # ---------------------------------------------------------------------------- #

# # --------------------------------- add plot --------------------------------- #
# window.setCentralWidget(plot_widget)
# window.show()

# app.exec()
#! ---------------------------------------------------------------------------- #
#!                                     case4                                    #
#! ---------------------------------------------------------------------------- #
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super(ViewBox,self).__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        # self.enableAutoRange(x=False, y=False) # 자동 range (add)
        # self.setAutoVisible(x=False, y=False)  # 자동 min max
        
    # def wheelEvent(self, event):
    #     x_min, x_max = self.viewRange()[0]
    #     x_rng = (x_max - x_min) * 0.1
        
    #     if event.delta() < 0:
    #         self.setXRange(x_min - x_rng , x_max, padding=0)
    #     else:
    #         self.setXRange(x_min + x_rng , x_max, padding=0)

class  PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.plot_item = self.getPlotItem()

        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 

        self.data_item = pg.PlotCurveItem(x,y,antialias=True)

        self.plot_item.addItem(self.data_item)
        self.plot_item.showAxis('right')


app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()

plot_widget = PlotWidget(viewBox=ViewBox())

window.setCentralWidget(plot_widget)
window.show()

app.exec()

























#$ ---------------------------------------------------------------------------- #
#$                                      gen                                     #
#$ ---------------------------------------------------------------------------- #
import datetime
def create_weekdays(start_date, num_days):
    current_date = start_date
    weekdays = []
    while len(weekdays) < num_days:
        if current_date.weekday() < 5:  # 월요일(0)부터 금요일(4)까지
            weekdays.append(current_date)
        current_date += datetime.timedelta(days=1)
    return weekdays
start_date = datetime.date(2024, 1, 1)
weekdays = create_weekdays(start_date, 10)
print(weekdays[0].strftime("%y-%m-%d"))
#! ---------------------------------------------------------------------------- #
#!                               case4 : setTicks                               #
#! ---------------------------------------------------------------------------- #
# app = QtWidgets.QApplication([])
# # ---------------------------------- window ---------------------------------- #
# window = QtWidgets.QMainWindow()
# # --------------------------------- gen plot --------------------------------- #
# x = np.arange(10, dtype=float)
# y = np.random.normal(size=10)
# y += 5 * np.sin(x/100) 
# d = create_weekdays(start_date, 10)

# t=list()
# for xx , dd in zip(x,d):
#     t.append((xx,dd.strftime("%m-%d")))

# print(t)
# # ---------------------------------------------------------------------------- #

# plot_widget = pg.PlotWidget()
# plot_item = plot_widget.getPlotItem()
# plot_item.showGrid(x=True,y=True)


# view_box = plot_item.getViewBox()
# view_box.enableAutoRange(y=False)
# view_box.enableAutoRange(y=True) # 자동 range (add)
# view_box.setAutoVisible(y=True)  # 자동 min max

# axis_x = plot_item.getAxis('bottom')
# axis_x.setTicks([t])

# data_item = pg.PlotCurveItem(x,y,antialias=True)
# plot_item.addItem(data_item)

# # --------------------------------- add plot --------------------------------- #
# window.setCentralWidget(plot_widget)
# window.show()

# app.exec()


# app = QtWidgets.QApplication([])

# # 주말을 제외한 날짜 데이터 생성
# start_date = datetime.date(2024, 1, 1)
# num_points = 10  # 데이터 포인트 수
# weekdays = create_weekdays(start_date, num_points)
# x_dates = [datetime.datetime.combine(date, datetime.datetime.min.time()) for date in weekdays]
# x_timestamps = [dt.timestamp() for dt in x_dates]

# # 날짜에 해당하는 y값 생성
# y = np.random.normal(size=num_points)
# y += 5 * np.sin(np.array(x_timestamps)/100) 

# # PlotWidget 및 PlotItem 설정
# window = QtWidgets.QMainWindow()
# plot_widget = pg.PlotWidget()
# plot_item = plot_widget.getPlotItem()

# # 사용자 정의 날짜 축 설정
# axis = pg.DateAxisItem(orientation='bottom')
# plot_item.setAxisItems({'bottom': axis})

# # 데이터 플로팅
# data_item = pg.PlotCurveItem(x_timestamps, y, antialias=True)
# plot_item.addItem(data_item)

# # 윈도우 설정
# window.setCentralWidget(plot_widget)
# window.show()

# app.exec_()