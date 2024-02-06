from PySide6 import QtWidgets, QtCore

import pyqtgraph as pg
import numpy as np

# from pyqtgraph.Qt import QtCore, QtGui


class CandleItem(pg.GraphicsObject):
    def __init__(self):
        super().__init__()
        self.w_body = 0.8
        self.data = np.empty((0,5))

    def set_data(self, data):
        """[index, open, high, low, close]"""
        self.data = data
        self.gen_picture()
        self.update() # 변경 사항을 적용하고, 재그리기 요청

    def gen_data(self, ohlc:list|tuple):
        arr = np.array(ohlc)
        if arr.ndim == 1:
            narr = arr.reshape(1,5)
        elif arr.ndim == 2:
            narr = arr
        else:
            Warning("invalid data dim")
        return narr

    def gen_picture(self):
        self.picture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)
        p.setRenderHint(pg.QtGui.QPainter.Antialiasing)

        if self.data.size > 0 :
            for (index, open, high, low, close ) in self.data:
                if open > close:
                    p.setPen(pg.mkPen('r'))
                    p.setBrush(pg.mkBrush('r'))
                else:
                    p.setPen(pg.mkPen('b'))
                    p.setBrush(pg.mkBrush('b'))
                p.drawLine(pg.QtCore.QPointF(index, low), pg.QtCore.QPointF(index, high))
                p.drawRect(pg.QtCore.QRectF(index - self.w_body/2, open, self.w_body, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.picture.boundingRect())
    
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=False, y=False) # 자동 range (add)
        self.setAutoVisible(x=False, y=False)  # 자동 min max

    def wheelEvent(self, event):
        # 확대/축소 비율 설정
        x_min, x_max = self.viewRange()[0]
        # print(x_min, x_max)
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() < 0:
            # self.scaleBy((1/factor, 1))
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)
    

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.data_candle = np.empty((0,5))          #@ index , open, high, low, close
        self.data_crosshair = pg.QtCore.QPointF(0,0)   #@ last pos

        self.showGrid(x=True,y=True)
        # ----------------------------- dataitem ----------------------------- #
        self.plotitem =  self.getPlotItem()

        # candle
        self.candle = CandleItem()
        self.plotItem.addItem(self.candle)

        # cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plotItem.addItem(self.vLine)
        self.plotItem.addItem(self.hLine)
        # self.addItem(self.vLine, ignoreBounds=True)
        # self.addItem(self.hLine, ignoreBounds=True)  

        self.scene().sigMouseMoved.connect(self.mouseMoved)
        self.getViewBox().sigRangeChanged.connect(self.rangeChanged)
        # -------------------------------------------------------------------- #

    def update_dataitem(self, ohlc:tuple|list):
        data_candle = self.candle.gen_data(ohlc=ohlc)
        self.data_candle = np.append(self.data_candle, data_candle, axis=0)
        self.candle.set_data(self.data_candle)

    def amend_dataitem(self, ohlc:tuple|list):
        data_candle = self.candle.gen_data(ohlc=ohlc)
        self.data_candle[-1] = data_candle
        self.candle.set_data(self.data_candle)

    def update_yrange_given_xrange(self):
        x_min, x_max = self.getViewBox().viewRange()[0]
        y_min, y_max = self.getViewBox().viewRange()[1]

        # xdata = self.plot_dataitem.getData()[0]
        # ydata = self.plot_dataitem.getData()[1]

        # ydata_given_xrange = ydata[(xdata >= x_min) & (xdata <= x_max)]
        mask_min = self.data_candle[:,0] >= x_min
        mask_max = self.data_candle[:,0] <= x_max
        filtered_rows = self.data_candle[mask_min&mask_max]

        # if len(ydata_given_xrange)>0:
        #     y_min_new = min(ydata_given_xrange)
        #     y_max_new = max(ydata_given_xrange)
        if filtered_rows.size>0:
            y_max_new = np.max(filtered_rows[:, 2]) #@ high        
            y_min_new = np.min(filtered_rows[:, 3]) #@ low        
            if not (y_min_new == y_min and y_max_new == y_max):
                self.setYRange(y_min_new, y_max_new)
                
    def update_xrange_minmax(self, x_min=None):
        # xdata = self.plot_dataitem.getData()[0]
        x_end = np.max(self.data_candle[:,0]) 
        x_sta = np.min(self.data_candle[:,0]) if x_min is None else x_end - x_min 
        self.setXRange(x_sta, x_end, padding=0.05)
        
    def update_xrange_window(self):
        x_min, x_max = self.getViewBox().viewRange()[0]
        # xdata = self.plot_dataitem.getData()[0]
        threshold = (x_max-x_min)*0.05 
        
        if x_max - threshold <= self.data_candle[-1,0] <= x_max + 1 :
        # if x_max - threshold <= len(xdata) <= x_max + 1 :
            self.setXRange(x_min + threshold, x_max + threshold, padding=0)

    def update_crosshair(self):
        mousePoint = self.plotItem.vb.mapSceneToView(self.data_crosshair)
        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

    # ------------------------------- callback ------------------------------- #
    def mouseMoved(self, evt):
        self.data_crosshair = evt         #? curr pos for timer
        self.update_crosshair()

    def rangeChanged(self):
        self.update_crosshair()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.plotwidget = PlotWidget(viewBox=ViewBox())
        self.setCentralWidget(self.plotwidget)

        # -------------------------------------------------------------------- #
        data = list()
        self.prev = None
        for i in range(1000):
            i_data = generate_candlestick_data(i, self.prev)
            self.prev = i_data[-1]
            data.append(i_data)
        # from pprint import pprint
        # pprint(data)
        # np.array(data)
        self.plotwidget.update_dataitem(data)
        self.plotwidget.update_xrange_minmax(50)
        self.plotwidget.update_yrange_given_xrange()
        # -------------------------------------------------------------------- #

        self.timer = pg.QtCore.QTimer()
        self.timer.setInterval(500)  # 500 밀리초마다 업데이트
        self.timer.timeout.connect(self.update)
        self.timer.start()

        self.test_cnt = 1
        
    def update(self):
        # print(self.plotwidget.data_candle)
        i_data = generate_candlestick_data(self.plotwidget.data_candle[-1,0]+1, self.prev)
        self.prev = i_data[-1] 

        #@ test---------------------------
        # if self.test_cnt % 5 == 0:
        #     self.plotwidget.update_dataitem(x_new, y_new)
        #     self.test_cnt = 1
        # else:
        #     self.plotwidget.amend_dataitem(x_new, y_new)
        #     self.test_cnt += 1

        #@ test---------------------------
        # print(i_data)
        self.plotwidget.update_dataitem(i_data)
        self.plotwidget.update_xrange_window()
        self.plotwidget.update_yrange_given_xrange()


import random
def generate_candlestick_data(i,previous_close=None):
    """
    보다 정교한 캔들스틱 데이터를 생성하는 함수입니다.
    이전 캔들스틱의 종가를 참조하여 다음 캔들스틱의 시가를 결정할 수 있습니다.
    """
    if previous_close is None:
        open_price = random.uniform(100, 200)
    else:
        # 이전 종가 근처에서 변동성을 고려하여 시가 결정
        open_price = previous_close * random.uniform(0.95, 1.05)

    # 종가는 시가 대비 일정 범위 내에서 결정
    close_price = open_price * random.uniform(0.95, 1.05)

    # 고가와 저가는 시가/종가를 기준으로 일정 범위 내에서 결정
    high_price = max(open_price, close_price) * random.uniform(1.0, 1.1)
    low_price = min(open_price, close_price) * random.uniform(0.9, 1.0)

    return (
        i,
        open_price,
        high_price,
        low_price,
        close_price
    )
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

# import numpy as np
# data = list()
# prev = None
# for i in range(5):
#     i_data = generate_candlestick_data(i, prev)
#     prev = i_data[-1]
#     data.append(i_data)

# arr = np.array(data)
# arr
# if arr.ndim == 1:
#     narr = arr.reshape(1,5)
# elif arr.ndim == 2:
#     narr = arr
# else:
#     Warning("invalid data dim")

# data = list()
# prev = None
# for i in range(100):
#     i_data = generate_candlestick_data(i, prev)
#     prev = i_data[-1]
#     data.append(i_data)

# np.array(data)
import numpy as np

data = [
    (1., 10, 13, 5, 15),
    (2., 13, 17, 9, 20),
    (3., 17, 14, 11, 23),
    (4., 1, 1, 1, 1),
    # 여기에 더 많은 데이터를 추가할 수 있습니다.
]
data_candle = np.array(data)
np.max(data_candle[:,2])
data_candle[0,-1]

# self.data_candle[:,0] > 1
# self.data_candle[:,0] > 4
# self.data_candle[(self.data_candle[:,0] > 1) &(self.data_candle[:,0] < 4)]

# ndata = np.array([(4., 1, 1, 1, 1)])

# ndata.ndim
# ndata.shape

# self.data_candle
# self.data_candle[-1] = ndata

# self.data_candle
# # data = [1, 2, 3]


# np.array(data).ndim
# np.array(data).ndim


# import numpy as np

# arr = np.empty((0,5))
# arr
# arr = np.append(arr, np.array([[0,0,0,0,0]]), axis=0)
# arr = np.append(arr, np.array([np.array([0,0,0,0,0])]), axis=0)

# arr


# dd = np.array([1,2,3])
# dd.ndim
# np.array(dd).ndim

# np.array([[0,0,0,0,0]]).shape

# np.array([data]).shape

# np.array(data)


# arr = np.empty((0,3), int)
# arr
# arr = np.append(arr, np.array([[1, 2, 3]]), axis=0)
# arr
# np.append(arr, np.array([[1, 2, 3]]), axis=0)
# np.append(arr, np.array([[1, 2, 3]]), axis=0)
# np.append(arr, np.array([data]), axis=0)



# arr
# arr.size

# if arr :
#     print(1)
# else:
#     print(2)
# arr = np.append(arr, np.array([[0,0,0,0,0]]), axis=0)


# arr = np.append(arr, np.array([[1, 2, 3]]), axis=0)
# arr = np.append(arr, np.array([[1, 2, 3]]), axis=0)
# arr = np.append(arr, np.array([[4, 5, 0]]), axis=0)


# # print(arr)

# for ar in arr:
#     print(ar)

# for a, b, c in arr:
#     print(a,b,c)