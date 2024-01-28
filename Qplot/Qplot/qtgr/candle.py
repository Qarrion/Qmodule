
import pyqtgraph as pg
import numpy as np

from pyqtgraph import QtCore, QtGui
import random

class CandlestickItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        # self.data = data  ## data must have fields: time, open, close, min, max
        self.data = np.empty((0,5))
        self._w_body = 0.8
        # self.generatePicture()

    def generate_candlestick_data(self, x):
        # 임의의 캔들스틱 데이터 생성
        open = random.uniform(10, 20)
        close = open + random.uniform(-2, 2)
        low = min(open, close) - random.uniform(0, 2)
        high = max(open, close) + random.uniform(0, 2)
        return {'x': x, 'open': open, 'high': high, 'low': low, 'close': close}
    
    # TODO crosshair 가 힌트!     
    def generatePicture(self):
        ## pre-computing a QPicture object allows paint() to run much more quickly, 
        ## rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))

        # w = (self.data[1][0] - self.data[0][0]) / 3.
        w = 0.8 
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QtCore.QRectF(t-w/2, open, w, close-open))
        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        # 아이템이 차지하는 전체 영역을 정의
        ## boundingRect _must_ indicate the entire area that will be drawn on
        ## or else we will get artifacts and possibly crashing.
        ## (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())
    
data = [  ## fields are (time, open, close, min, max).
    (1., 10, 13, 5, 15),
    (2., 13, 17, 9, 20),
    (3., 17, 14, 11, 23),
    (4., 14, 15, 5, 19),
    (5., 15, 9, 8, 22),
    (6., 9, 15, 8, 16),
]

item = CandlestickItem()
plt = pg.plot()
plt.addItem(item)
plt.setWindowTitle('pyqtgraph example: customGraphicsItem')