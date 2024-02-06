from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
import pyqtgraph as pg
import numpy as np

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super(ViewBox,self).__init__(*args, **kwds)
        # self.enableAutoRange()
        # self.setMouseEnabled(y=False)
        # self.enableAutoRange(x=False, y=True) # 자동 range (add)
        self.setAutoVisible(x=False, y=False)  # 자동 min max
        
    # def wheelEvent(self, event):
    #     x_min, x_max = self.viewRange()[0]
    #     x_rng = (x_max - x_min) * 0.1
        
    #     if event.delta() < 0:
    #         self.setXRange(x_min - x_rng , x_max, padding=0)
    #     else:
    #         self.setXRange(x_min + x_rng , x_max, padding=0)

class AxisItem(pg.AxisItem):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def tickStrings(self, values, scale, spacing):
        self._strings = super().tickStrings(values, scale, spacing)
        # self._values = values
        print('value', values)
        print('string', self._strings)
        return self._strings

    def tickValues(self, minVal, maxVal, size):
        self._values = super().tickValues(minVal, maxVal, size)
        print(self._values)
        # print(self._values)
        return self._values
    
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        # 기본 틱과 텍스트 그리기
        super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
        
        # 특정 틱 레벨에 대한 추가적인 그리기 작업
        p.setPen(pg.mkPen(None))  # 틱에 대한 펜 설정
        for rect, flags, text in textSpecs:
            # print(rect)
            if "특정 조건":  # 여기에 특정 조건을 추가
                p.setBrush(pg.mkBrush('r'))  # 여기서 '배경색'을 원하는 색상으로 변경하세요.
                p.setPen(pg.mkPen(None))  # 테두리 없음
                p.drawRect(rect)  # 배경 사각형 그리기

                # 텍스트 그리기
                p.setPen(self.textPen())  # 텍스트 색상 설정
                p.drawText(rect, int(flags), text)

class  PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.plot_item = self.getPlotItem()

        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 

        self.data_item = pg.PlotCurveItem(x,y,antialias=True)


        self.plot_item.addItem(self.data_item)
        self.plot_item.showAxis('right')

        self.axis_l = AxisItem('left')
        self.plot_item.setAxisItems({'left':self.axis_l})

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        mousePoint = self.plot_item.vb.mapSceneToView(event.position())
        y_value = mousePoint.y()

        # [(20.0, [0.0]), (10.0, []), (2.0, [-8.0, -6.0, -4.0, -2.0, 2.0, 4.0, 6.0])]
        ticks = []
        for lev in self.axis_l._values:
            ticks.append([(v, f"{v:.2f}") for v in lev[1]])
        # ticks.append([(y_value, f"{y_value:.2f}")])
        ticks[-1].append((y_value, f"{y_value:.2f}"))
        # print(ticks)
        self.plot_item.getAxis('left').setTicks(ticks)
        # self.plot_item.getAxis('left')
        # new_tick = (y_value, f'NewTick: {y_value:.2f}')
        # self.plot_item.getAxis('left').setTicks([[(1, 'Tick1'), (2, 'Tick2'), (3, 'Tick3'), (4, 'Tick4'), (5, 'Tick5'), new_tick]])

    #     print(y_value)
        
app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()

plot_widget = PlotWidget(viewBox=ViewBox())

window.setCentralWidget(plot_widget)
window.show()

app.exec()
