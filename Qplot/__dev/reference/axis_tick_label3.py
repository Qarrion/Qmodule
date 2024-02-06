from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QRectF
import pyqtgraph as pg
import sys

class CustomAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(CustomAxisItem, self).__init__(*args, **kwargs)
        self.mouse_scene = None

    def updateMousePosition(self, pos):
        self.mouse_scene = pos
        self.picture = None  # 이것은 다시 그리기 위해 필요합니다.
        self.update()

    def tickStrings(self, values, scale, spacing):
        tstr = super().tickStrings(values, scale, spacing)        
        tstr = [f"{s:.2f}" for s in values]
        return tstr
    
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
            super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
            if self.mouse_scene is not None:
                view = self.linkedView()  # 현재 축에 연결된 뷰를 가져옵니다.

                # ------------------------------------------------------------ #
                mouse_scene_y = self.mouse_scene.y()
                mouse_view = view.mapSceneToView(self.mouse_scene)
                mouse_view_y = mouse_view.y()  # 마우스의 Y 좌표를 가져옵니다.
                # print(mouse_view_y, mouse_scene_y)
                text = "{:.2f}".format(mouse_view_y)
                metrics = p.fontMetrics()
                textWidth = axisSpec[1].x()
                # textWidth = metrics.horizontalAdvance(text)
                textHeight = metrics.height()
                rect = QRectF(0, mouse_scene_y - textHeight / 2, textWidth, textHeight)

                # ------------------------------------------------------------ #
                print(axisSpec[1])     
                _ , flags , _ = textSpecs[0]
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.fillRect(rect.adjusted(-100, 0, 0, 0), QColor(100, 100, 250, 220))  # 배경색 적용
                p.drawText(rect, Qt.AlignCenter, text)  # 텍스트 재그리기
  
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
