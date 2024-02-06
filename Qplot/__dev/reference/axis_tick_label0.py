from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QApplication, QMainWindow
from PySide6.QtGui import QColor, QPainter
import pyqtgraph as pg
import sys

class CustomAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(CustomAxisItem, self).__init__(*args, **kwargs)

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        super(CustomAxisItem, self).drawPicture(p, axisSpec, tickSpecs, textSpecs)
        for rect, flags, text in textSpecs:
            if text == "0":  # 예를 들어, "0"에 해당하는 레이블을 찾음
                # 배경색을 가진 사각형 생성
                # bgRect = QGraphicsRectItem(rect)
                # bgRect.setBrush(QColor(100, 100, 250, 100))  # 배경색 설정
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                # p.fillRect(rect.adjusted(-30, -2, 30, 2), QColor(100, 100, 250, 100))  # 배경색 적용
                p.fillRect(rect.adjusted(-100, -5, 5, 5), QColor(100, 100, 250, 100))  # 배경색 적용
                p.drawText(rect, flags, text)  # 텍스트 재그리기

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        graphWidget = pg.PlotWidget(axisItems={'left': CustomAxisItem(orientation='left')})
        self.setCentralWidget(graphWidget)

        x = range(10)
        y = [5, -2, 0.00, 3, -1, 6, -3, 2, 0, 4]
        graphWidget.plot(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())