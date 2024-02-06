import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
import pyqtgraph as pg

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)  # 마우스 추적 활성화

    def mouseMoveEvent(self, event):
        # 현재 마우스 위치의 뷰 좌표를 얻습니다.
        pos = event.position()  # PySide6에서는 event.pos() 대신 event.position()을 사용
        view_coords = self.plotItem.vb.mapSceneToView(pos)

        # 데이터 좌표계는 뷰 좌표계와 같게 됩니다.
        data_coords = (view_coords.x(), view_coords.y())

        # 장면 좌표계
        scene_coords = (pos.x(), pos.y())

        print("-----------------------------------------------")
        print(f"Scene Coordinates: {scene_coords}")
        print(f"View Coordinates: ({view_coords.x()}, {view_coords.y()})")
        print(f"Data Coordinates: {data_coords}")

        print(f"View to Scene: {self.mapToScene(*data_coords)}") #! int


        super().mouseMoveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # CustomPlotWidget 생성 및 설정
        self.graphWidget = CustomPlotWidget()
        self.setCentralWidget(self.graphWidget)

        # 예제 데이터 플로팅
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        self.graphWidget.plot(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

# import sys
# from PySide6.QtWidgets import QApplication, QMainWindow
# import pyqtgraph as pg

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         self.graphWidget = pg.PlotWidget()
#         self.setCentralWidget(self.graphWidget)

#         # 데이터 추가
#         self.graphWidget.plot([1], [1], symbol='o')

#         # 마우스 이벤트 연결
#         self.graphWidget.scene().sigMouseClicked.connect(self.onClick)

#     def onClick(self, event):
#         # 데이터 포인트 (1,1)에 대한 뷰 좌표계 위치를 가져옵니다.
#         plot_pos = pg.Point(1,1)
#         view_pos = self.graphWidget.plotItem.vb.mapViewToScene(plot_pos)
#         scene_pos = self.graphWidget.plotItem.vb.mapToView(plot_pos)
#         # 장면 좌표계 위치
#         # 플롯 좌표계는 이미 알고 있는 데이터 포인트입니다.

#         view_pos2 = self.graphWidget.plotItem.vb.mapFromScene(scene_pos)
#         # scenePos  = self.graphWidget.plotItem.vb.mapToScene(viewCoords)
#         print(f"Plot Coordinates: {plot_pos}")
#         print(f"View1 Coordinates: {view_pos}")
#         print(f"View2 Coordinates: {view_pos2}")

#         print(f"Scene1 Coordinates: {scene_pos}")
#         print(f"Scene2 Coordinates: {scene_pos}")
        
#         print("# -------------------------------------------------------------------- #")




# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main = MainWindow()
#     main.show()
#     sys.exit(app.exec())