import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQtGraph InfiniteLine with Label Example")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # PyQtGraph 그래프 위젯 생성
        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        # 그래프 생성
        self.plot = self.graphWidget.plot([1, 2, 3, 4, 5], [10, 20, 30, 40, 50], pen='b', name='Data')
        self.graphWidget.setLabel('left', 'Y-Axis', units='units')
        self.graphWidget.setLabel('bottom', 'X-Axis', units='units')

        # 무한선 생성 (수직 무한선)
        self.vLine = pg.InfiniteLine(pos=2, angle=90, movable=True)

        # 마우스 이벤트를 연결하여 무한선 위치와 라벨 업데이트
        self.proxy = pg.SignalProxy(self.graphWidget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        # 무한선을 그래프에 추가
        self.graphWidget.addItem(self.vLine)

        # 무한선과 연관된 라벨을 생성
        self.label = pg.TextItem("", anchor=(1, 1))
        self.graphWidget.addItem(self.label)

    def mouseMoved(self, event):
        pos = event[0]  # 마우스 위치 얻기
        if self.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget.plotItem.vb.mapSceneToView(pos)
            x, y = mousePoint.x(), mousePoint.y()

            # 마우스 위치에 따라 무한선 이동 및 라벨 업데이트
            self.vLine.setPos(x)
            self.label.setText(f"X={x:.2f}")  # 소수점 두 자리까지 표시
            y_axis_min = self.graphWidget.plotItem.viewRange()[1][0] 
            self.label.setPos(x, y_axis_min)  # x 위치에 라벨 표시, y 위치는 그래프의 아래로 설정

def main():
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
