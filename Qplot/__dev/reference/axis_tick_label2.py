from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QRectF
import pyqtgraph as pg
import sys

class CustomAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(CustomAxisItem, self).__init__(*args, **kwargs)
        self.currentMousePosition = None

    def updateMousePosition(self, pos):
        self.currentMousePosition = pos
        self.picture = None  # 이것은 다시 그리기 위해 필요합니다.
        self.update()

    def tickStrings(self, values, scale, spacing):
        tstr = super().tickStrings(values, scale, spacing)        
        tstr = [f"{s:.2f}" for s in values]
        return tstr
    
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
            super(CustomAxisItem, self).drawPicture(p, axisSpec, tickSpecs, textSpecs)
            if self.currentMousePosition is not None:
                view = self.linkedView()  # 현재 축에 연결된 뷰를 가져옵니다.
                mousePoint = view.mapSceneToView(self.currentMousePosition)
                mouseY = mousePoint.y()  # 마우스의 Y 좌표를 가져옵니다.
                print(mouseY)
                text = "{:.2f}".format(mouseY)
                metrics = p.fontMetrics()
                textWidth = metrics.horizontalAdvance(text)
                textHeight = metrics.height()
                rect = QRectF(0, mouseY - textHeight / 2, textWidth + 6, textHeight)
                                     
                _ , flags , _ = textSpecs[0]
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.fillRect(rect.adjusted(-100, -5, 5, 5), QColor(100, 100, 250, 100))  # 배경색 적용
                p.drawText(rect, flags, text)  # 텍스트 재그리기
                print(rect)
                # print(rect)
                # p.setPen(pg.mkPen('r'))
                # p.drawLine(axisSpec[0], mouseY, axisSpec[1], mouseY)
                    # # p.setPen(pg.mkPen('r'))  # 틱과 텍스트의 색상을 설정합니다.
                    # p.fillRect(rect.adjusted(-100, -5, 5, 5), QColor(100, 100, 250, 100))
                    # # p.drawLine(axisSpec[0], mouseY, axisSpec[1], mouseY)  # Y 축에 새로운 틱을 그립니다.

            #         # Y 축 틱과 텍스트를 마우스 위치에 맞게 그립니다.
            #         p.drawText(axisSpec[1] + 2, mouseY, "{:.2f}".format(mouseY))  # 틱 옆에 Y 값 표시

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.graphWidget = pg.PlotWidget(axisItems={'left': CustomAxisItem(orientation='left')})
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.scene().sigMouseMoved.connect(self.onMouseMoved)

        x = range(10)
        y = [5, -2, 0, 3, -1, 6, -3, 2, 0, 4]
        self.graphWidget.plot(x, y)

    def onMouseMoved(self, pos):
        axisItem = self.graphWidget.getAxis('left')
        if isinstance(axisItem, CustomAxisItem):
            axisItem.updateMousePosition(pos)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
