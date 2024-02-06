from PySide6 import QtWidgets
import pyqtgraph as pg
import numpy as np
# ---------------------------------------------------------------------------- #
# import pyqtgraph as pg
# from PySide6.QtWidgets import QApplication

# app = QApplication([])
# plot_widget = pg.PlotWidget()

# # PlotItem에 접근
# plot_item = plot_widget.getPlotItem()

# # 각 축의 AxisItem에 접근
# left_axis = plot_item.getAxis('left')
# bottom_axis = plot_item.getAxis('bottom')
# right_axis = plot_item.getAxis('right')
# top_axis = plot_item.getAxis('top')

# # 예시: 축의 레이블 변경
# left_axis.setLabel('Y축 레이블')
# bottom_axis.setLabel('X축 레이블')

# plot_widget.show()
# app.exec()
# ---------------------------------------------------------------------------- #
#! ---------------------------------------------------------------------------- #
#!                                     case4                                    #
#! ---------------------------------------------------------------------------- #
class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super(ViewBox,self).__init__(*args, **kwds)
        # self.enableAutoRange()
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=True, y=True) # 자동 range (add)
        self.setAutoVisible(x=True, y=True)  # 자동 min max
        
    def wheelEvent(self, event):
        x_min, x_max = self.viewRange()[0]
        x_rng = (x_max - x_min) * 0.1
        
        if event.delta() < 0:
            self.setXRange(x_min - x_rng , x_max, padding=0)
        else:
            self.setXRange(x_min + x_rng , x_max, padding=0)


class AxisItem(pg.AxisItem):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def tickStrings(self, values, scale, spacing):
        # 표준 틱 문자열 생성
        strings = super().tickStrings(values, scale, spacing)

        # print(strings)

        # for val, s in zip(values, strings):
        return strings
    
    def tickValues(self, minVal, maxVal, size):
        self._values = super().tickValues(minVal, maxVal, size)
        print(self._values)
        # print(self._values)
        return self._values
        # 특정 값에 대한 문자열 추가
        # new_strings = []
        # for val, s in zip(values, strings):
        #     if val == 50:  # 예를 들어, 값이 50인 틱에 추가 문자열 적용
        #         new_s = f"{s} (특별값)"
        #     else:
        #         new_s = s
        #     new_strings.append(new_s)
        # return new_strings
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
            #! profiler = debug.Profiler()

            p.setRenderHint(p.RenderHint.Antialiasing, False)
            p.setRenderHint(p.RenderHint.TextAntialiasing, True)

            ## draw long line along axis
            pen, p1, p2 = axisSpec
            p.setPen(pen)
            p.drawLine(p1, p2)
            #! p.translate(0.5,0)  ## resolves some damn pixel ambiguity

            ## draw ticks
            for pen, p1, p2 in tickSpecs:
                p.setPen(pen)
                p.drawLine(p1, p2)
                print(p1, p2)
            # profiler('draw ticks')

            # Draw all text
            if self.style['tickFont'] is not None:
                p.setFont(self.style['tickFont'])
            p.setPen(self.textPen())
            bounding = self.boundingRect().toAlignedRect()
            p.setClipRect(bounding)
            for rect, flags, text in textSpecs:
                p.drawText(rect, int(flags), text)

        #! profiler('draw text')


    # def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
    #     # 기본 축 그리기
    #     super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
        
    #     # p.setPen(axisSpec['pen'])
    #     # p.drawLine(axisSpec['p1'], axisSpec['p2'])

    #     # 틱 그리기
    #     p.setPen(self.pen)
    #     for tickPos, tickLength, tickLevel in tickSpecs:
    #         if tickLevel == 0:  # 메이저 틱
    #             p.drawLine(tickPos, tickPos + pg.Point(0, -tickLength))
    #         else:  # 마이너 틱
    #             p.drawLine(tickPos, tickPos + pg.Point(0, -tickLength / 2))

    #     # 레이블 그리기
    #     for rect, flags, text in textSpecs:
    #         p.drawText(rect, flags, text)
class  PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.plot_item = self.getPlotItem()
        self.plot_item.showAxis('right')

        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)
        y += 5 * np.sin(x/100) 

        self.data_item = pg.PlotCurveItem(x,y,antialias=True)
        self.axis_left = AxisItem('left')

        self.plot_item.addItem(self.data_item)
        self.plot_item.setAxisItems({'left':self.axis_left})
        # self.plot_item.showAxis('right')

        # self.it = pg.TextItem('hi', fill=pg.mkBrush('r'), anchor=(1,1))

    # def mouseMoveEvent(self, event):
    #     mousePoint = self.plot_item.vb.mapSceneToView(event.position())
    #     y_value = mousePoint.y()
        # dd=self.plot_item.getAxis('left')
        # print(dd)
        # print(y_value)
        # self.tickviewer.setTickValue()

app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()


plot_widget = PlotWidget(viewBox=ViewBox())
# axis = AxisItem(orientation='left')
# plot_widget = PlotWidget(viewBox=ViewBox(),axisItems={'left': axis})

window.setCentralWidget(plot_widget)
window.show()

app.exec()
