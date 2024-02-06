import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
import pyqtgraph as pg

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMouseTracking(True)  # 마우스 추적 활성화

    def mouseMoveEvent(self, event):
        # 마우스 위치를 가져와서 Y축 값을 계산
        pos = event.position()  # 변경된 부분
        yValue = self.plotItem.vb.mapSceneToView(pos).y()
        self.parent().updateMousePosition(yValue)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # CustomPlotWidget 생성 및 설정
        self.graphWidget = CustomPlotWidget(self)
        self.setCentralWidget(self.graphWidget)

        # Y축 위치를 표시할 레이블 생성
        self.mousePositionLabel = QLabel(self)
        self.mousePositionLabel.move(10, 10)

        # 데이터 플롯
        self.graphWidget.plot([0, 1, 2, 3, 4, 5], [30, 32, 34, 32, 33, 31])

    def updateMousePosition(self, yValue):
        # 마우스 위치 업데이트
        self.mousePositionLabel.setText(f"Y: {yValue:.2f}")

app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
