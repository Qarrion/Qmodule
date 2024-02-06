from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from PySide6.QtGui import QBrush, QPen
from PySide6.QtCore import Qt, QRectF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # QGraphicsScene 생성
        self.scene = QGraphicsScene(self)

        # 여기에 그래픽 항목을 추가
        # 예를 들어, 사각형을 추가합니다.
        rect = QRectF(0, 0, 100, 100)
        brush = QBrush(Qt.blue)
        self.scene.addRect(rect, QPen(Qt.black), brush)

        # 텍스트 항목 추가
        self.scene.addText("Hello, QGraphicsScene!")

        # QGraphicsView 설정
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # 윈도우 크기 조정
        self.setGeometry(100, 100, 800, 600)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()