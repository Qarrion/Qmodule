import sys
from PySide6 import QtWidgets
import pyqtgraph as pg
import datetime
import numpy as np


# 정수 x축 데이터 및 y축 데이터 생성
x = np.arange(10)
y = np.array([1,0,2,0,3,0,4,0,5,0])
def create_weekdays(start_date, num_days):
    current_date = start_date
    weekdays = []
    while len(weekdays) < num_days:
        if current_date.weekday() < 5:  # 월요일(0)부터 금요일(4)까지
            weekdays.append(current_date)
        current_date += datetime.timedelta(days=1)
    return weekdays
start_date = datetime.date(2024, 1, 1)
d = create_weekdays(start_date, 10)
# d
# ---------------------------------------------------------------------------- #
class DateAxis(pg.AxisItem):
    def __init__(self, dates, *args, **kwargs):
        super(DateAxis, self).__init__(*args, **kwargs)
        self.dates = dates  # 날짜 데이터
        
    
    def tickStrings(self, values, scale, spacing):
        # print(values)
        return [self.dates[int(value)].strftime('%Y-%m-%d') if int(value) < len(self.dates) else '' for value in values]
    
# ---------------------------------------------------------------------------- #
app = QtWidgets.QApplication([])

window = QtWidgets.QMainWindow()
plot_widget = pg.PlotWidget()
plot_item = plot_widget.getPlotItem()

# 사용자 정의 축 적용
axis = DateAxis(d, orientation='bottom')
plot_item.setAxisItems({'bottom': axis})
plot_item.showGrid(x=True,y=True)
# x, y 데이터
x = np.arange(10)
y = np.array([1,0,2,0,3,0,4,0,5,0])

# 데이터 플로팅
data_item = pg.PlotCurveItem(x, y, symbol='o')
plot_item.addItem(data_item)

window.setCentralWidget(plot_widget)
window.show()

sys.exit(app.exec())