from PySide6 import QtWidgets
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent
import pyqtgraph as pg
import random, sys
import numpy as np
from PySide6.QtCore import QTimer
# ---------------------------------- diagram --------------------------------- #
# https://pyqtgraph.readthedocs.io/en/latest/api_reference/uml_overview.html

# https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotitem.html
# PlotWidget.plot() -> PlotItem + plot() -> PlotDataItem , AddItem
"""

addItem 메서드를 사용하지 않고 데이터를 직접 업데이트하는 방식을 선택한 이유는 PyQtGraph에서 실시간 데이터 
스트리밍을 처리하는 특정 상황에 따라 달라질 수 있습니다. 각 방식은 그 자체의 장단점을 가지며, 상황에 따라 
적합한 방법을 선택하는 것이 중요합니다.

addItem 사용 시 장점 및 단점:
장점:

addItem은 플롯에 새로운 그래픽 요소(예: 라인, 점, 텍스트 등)를 추가할 때 사용됩니다.
여러 그래픽 요소를 동시에 관리하고 각각의 요소를 독립적으로 조작할 수 있는 경우에 유용합니다.
단점:

실시간 데이터 스트리밍에서는 addItem을 사용하여 데이터를 지속적으로 추가하면 성능 문제가 발생할 수 있습니다. 
각 addItem 호출은 새로운 그래픽 요소를 생성하고 이를 그래프에 추가하기 때문에, 데이터 포인트가 많아질수록 
렌더링에 더 많은 시간이 소요됩니다. 메모리 사용량이 증가할 수 있으며, 이는 대량의 데이터를 실시간으로 처리해야 
하는 경우에는 비효율적일 수 있습니다.


setData 사용 시 장점 및 단점:
장점:
setData는 기존 그래픽 요소(예: 라인)의 데이터를 갱신하는 데 사용됩니다.
실시간 데이터 스트리밍의 경우, setData를 사용하여 데이터 배열을 갱신하면 기존 그래픽 요소를 재사용하기 때문에 렌더링
성능이 개선됩니다. 메모리 사용량이 상대적으로 적고, 데이터 업데이트가 빠릅니다.

단점:
setData는 데이터 자체를 업데이트하는 것이므로, 그래픽 요소를 개별적으로 조작하거나 독립적으로 관리하는 것이 더 어렵습니다.
결론:
실시간 데이터 스트리밍과 같이 빈번하게 업데이트되는 데이터를 처리하는 경우에는 setData 방식이 성능 면에서 더 유리합니다.
반면, 여러 개별 그래픽 요소를 추가하고 각각을 독립적으로 관리해야 하는 상황에서는 addItem 방식이 적합할 수 있습니다.
따라서 사용하는 방법은 애플리케이션의 요구 사항과 성능 요구 사항에 따라 결정되어야 합니다.
"""

# https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/graphicsItems/ViewBox/ViewBox.html
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=True, y=True) # 자동 range (add)
        self.setAutoVisible(x=False, y=True)  # 자동 min max

    def wheelEvent(self, event):
        # 확대/축소 비율 설정
        x_min, x_max = self.viewRange()[0]
        print(x_min, x_max)
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() > 0:
            # self.scaleBy((1/factor, 1))
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)

# https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/widgets/PlotWidget.html#PlotWidget
# https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotitem.html
class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.x = np.array([])
        self.y = np.array([])
        self.plot_dataitem = self.plot(self.x,self.y,antialias=True)
        print(self.window)

    # def update_yaxis_given_xaxis(self):
    #     x_min, x_max = self.getViewBox().viewRange()[0]
    #     y_min, y_max = self.getViewBox().viewRange()[1]

    #     xdata = self.plot_dataitem.getData()[0]
    #     ydata = self.plot_dataitem.getData()[1]


    def update_dataitem(self, x, y):
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
        self.plot_dataitem.setData(self.x, self.y)

        # self.update_yaxis_given_xaxis()

        # x_min, x_max = self.getViewBox().viewRange()[0]
        # if x_max-50 <len(self.x) < x_max:
            # self.enableAutoRange(x=True, y=False)
            # self.setAutoVisible(x=False, y=True) # 자동 range (add)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pw = PlotWidget(viewBox=ViewBox())
        self.setCentralWidget(self.pw)

        # -------------------------------------------------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 
        self.pw.update_dataitem(x, y)
        # -------------------------------------------------------------------- #

        self.timer = QTimer()
        self.timer.setInterval(50)  # 500 밀리초마다 업데이트
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        x_new = len(self.pw.x)
        y_new = np.random.normal(size=1)[0] + 5 * np.sin(x_new/100) 
        self.pw.update_dataitem(x_new, y_new)






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()