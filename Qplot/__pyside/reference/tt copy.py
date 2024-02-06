import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from PySide6 import QtWidgets
class CandlestickItem(pg.GraphicsObject):
    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.data = [(0,0,0,0,0)] # data 형식: [(time, open, close, min, max), ...]
        self.generatePicture()

    def setData(self, data):
        self.data = data
        self.generatePicture()
        self.update() # 변경 사항을 적용하고, 재그리기 요청

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))

        w = 0.2  # 캔들스틱의 너비
        
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

# 사용 예시
if __name__ == '__main__':
    app = QtWidgets.QApplication()
    mw = QtWidgets.QMainWindow()
    cw = QtWidgets.QWidget()
    mw.setCentralWidget(cw)
    l = QtWidgets.QVBoxLayout()
    cw.setLayout(l)

    w = pg.PlotWidget()
    l.addWidget(w)

    data = [
        (1., 10, 13, 5, 15),
        (2., 13, 17, 9, 20),
        (3., 17, 14, 11, 23),
        # 여기에 더 많은 데이터를 추가할 수 있습니다.
    ]
    
    item = CandlestickItem()
    w.addItem(item)

    item.setData(data)

    mw.show()
    app.exec()