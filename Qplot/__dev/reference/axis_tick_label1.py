from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtCore import Qt
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

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        super(CustomAxisItem, self).drawPicture(p, axisSpec, tickSpecs, textSpecs)
        if self.currentMousePosition is not None:
            view = self.linkedView()
            if view is not None:
                mousePoint = view.mapSceneToView(self.currentMousePosition)
                mouseY = mousePoint.y()
                print(f"pos {self.currentMousePosition}, y {mouseY}")
                for rect, flags, text in textSpecs:
                    # 마우스 위치와 가장 가까운 tick 찾기
                    if abs(mouseY - float(text)) <= 0.5:  # 여기서는 tick 높이를 고려하여 조정할 수 있습니다.
                        print("--------------")
                        print(rect)
                        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        p.fillRect(rect.adjusted(-100, -5, 5, 5), QColor(100, 100, 250, 100))  # 배경색 적용
                        p.drawText(rect, flags, text)  # 텍스트 재그리기

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
