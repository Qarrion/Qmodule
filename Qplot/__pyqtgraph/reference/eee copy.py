import pyqtgraph as pg
from pyqtgraph import AxisItem
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter, QColor

class CustomAxis(AxisItem):
    def __init__(self, orientation, parent=None):
        AxisItem.__init__(self, orientation, parent)
        self.mouseY = None

    def setMouseY(self, y):
        self.mouseY = y

        self.update()

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        super(CustomAxis, self).drawPicture(p, axisSpec, tickSpecs, textSpecs)

        if self.mouseY is not None:
            p.setPen(pg.mkPen('r'))  # 마우스 위치 틱의 색상 설정
            # 마우스 위치에 대한 틱 값 계산
            tickValue = self.tickValues(0, self.length(), self.mouseY)[-1][1][0]
            tickText = self.tickStrings([tickValue], 0, 1)[0]
            # 틱 값 그리기
            print(tickValue, tickText)
            p.drawText(QPointF(0, self.mouseY), tickText)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.yAxis = CustomAxis("left")
        self.graphWidget.getPlotItem().setAxisItems({'left': self.yAxis})

        self.graphWidget.scene().sigMouseMoved.connect(self.onMouseMoved)

    def onMouseMoved(self, evt):
        pos = self.graphWidget.plotItem.vb.mapSceneToView(evt)
        self.yAxis.setMouseY(pos.y())

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
