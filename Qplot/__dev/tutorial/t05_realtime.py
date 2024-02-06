from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import numpy as np

class ViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseEnabled(y=False)
        self.enableAutoRange(x=False, y=False) #! 자동 range    autorange
        self.setAutoVisible(x=False, y=False)  #! 자동 min max  autorange
        # ['xMin', 'xMax', 'yMin', 'yMax', 'minXRange', 'maxXRange', 'minYRange', 'maxYRange']

        self.is_dragging = False

        # ------------------------------- wheel ------------------------------ #
        self.is_autorange = True
        self.timer_autorange = QtCore.QTimer()
        self.timer_autorange.setSingleShot(True)
        self.timer_autorange.timeout.connect(self.set_autorange_true) #* buffer *#

    def set_autorange_true(self):
        self.is_autorange = True
        print("set autorange!")

    def wheelEvent(self, event):
        self.is_autorange = False
        x_min, x_max = self.viewRange()[0]
        x_rng = (x_max - x_min) * 0.1
        x_min_new = x_min - x_rng if event.delta() < 0 else x_min + x_rng
        self.setXRange(x_min_new , x_max, padding=0)
        self.timer_autorange.start(1000)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.lastMousePosition = event.pos()
            self.is_autorange = False

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            currentPosition = event.pos()
            dx = currentPosition.x() - self.lastMousePosition.x()
            dy = currentPosition.y() - self.lastMousePosition.y()
            # self.chart().scroll(-dx, dy)
            self.translateBy(x=-dx, y=dy)
            self.lastMousePosition = currentPosition

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            self.timer_autorange.start(1000)

class AxisLeft(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse_scene = None

    def tickStrings(self, values, scale, spacing):
        # ------------------------------ format ------------------------------ #
        tstr = super().tickStrings(values, scale, spacing)        
        tstr = [f"{s:.2f}" for s in values]
        return tstr

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
        if self.mouse_scene is not None:
            text = f"{self.mouse_view_y:.2f}"
            textHeight = p.fontMetrics().height()
            # textWidth = axisSpec[1].x()
            textWidth = self.mapRectFromParent(self.geometry()).width()
            rect = QtCore.QRectF(0,self.mouse_scene_y - textHeight / 2, textWidth, textHeight)
            p.setPen(QtGui.QColor("#000000")) 
            p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            p.fillRect(rect.adjusted(-100, 0, 0, 0), QtGui.QColor("#f9d087"))
            p.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)


    def slot_mouse_moved(self, pos):
        self.update_position(pos)

    def update_position(self, pos):
        self.mouse_scene = pos
        view = self.linkedView() 
        self.mouse_scene_y = self.mouse_scene.y()
        self.mouse_view_y = view.mapSceneToView(self.mouse_scene).y()
        self.picture = None                                #* required redraw *# 
        self.update()                                      #* required redraw *#

class AxisRight(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_pos = None

    def tickStrings(self, values, scale, spacing):
        # ------------------------------ format ------------------------------ #
        tstr = super().tickStrings(values, scale, spacing)        
        tstr = [f"{s:.2f}" for s in values]
        return tstr

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        super().drawPicture(p, axisSpec, tickSpecs, textSpecs)
        # self.mouse_scene_y=278
        # self.mouse_view_y=-2

        if self.data_pos is not None:
            text = f"{self.mouse_view_y:.2f}"
            textHeight = p.fontMetrics().height()
            # textWidth = axisSpec[1].x()
            textWidth = self.mapRectFromParent(self.geometry()).width()
            rect = QtCore.QRectF(0,self.mouse_scene_y - textHeight / 2, textWidth, textHeight)

            p.setPen(QtGui.QColor("#000000")) 
            p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            p.fillRect(rect.adjusted(0, 0, 100, 0), QtGui.QColor(100, 100, 250, 220))
            p.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)
            # print(rect, self.mouse_scene_y, text)
            
    def slot_data_updated(self, pos):
        self.update_position(pos)

    def update_position(self, data_pos_y):
        # print(data_pos.y())
        self.data_pos = QtCore.QPointF(0, data_pos_y)
        view = self.linkedView() 
        self.mouse_scene_y = view.mapFromView(self.data_pos).y()
        self.mouse_view_y = self.data_pos.y()
        self.picture = None                                #* required redraw *# 
        self.update()                                      #* required redraw *#

class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        # ------------------------------ viewbox ----------------------------- #
        self.viewbox = ViewBox()
        kwargs.update({'viewBox':self.viewbox})          #* plotItem(viewBox) *#
        super().__init__(*args, **kwargs)
        # ----------------------------- autorange ---------------------------- #
        self.autorng = AutoRange(self.viewbox)          
        # ----------------------------- crosshair ---------------------------- #
        self.crosshair = CrossHair(self.viewbox)
        # ----------------------------- leadhair ----------------------------- #
        self.leadhair = LeadHair(self.viewbox)
        # ----------------------------- plotItem ----------------------------- #
        self.plotItem.showGrid(x=True, y=True)
        self.plotItem.showAxis('right')
        # ------------------------------- axis ------------------------------- #
        self.axix_left = AxisLeft('left')
        self.axix_right = AxisRight('right')
        self.plotItem.setAxisItems({'left':self.axix_left,'right':self.axix_right})

        # ------------------------------ signal ------------------------------ #
        self.scene().sigMouseMoved.connect(self.slot_mouse_moved)
        self.getViewBox().sigRangeChanged.connect(self.slot_range_changed)

        #@ ------------------------------- plot ------------------------------- #
        # -------------------------------------------------------------------- #
        self.data_line_x = np.array([])
        self.data_line_y = np.array([])
        self.plot_line =  pg.PlotCurveItem(
                                self.data_line_x,self.data_line_y,antialias=True)

        self.plotItem.addItem(self.plot_line)
        # -------------------------------------------------------------------- #

    def update_data(self, line_x, line_y, append=True):
        #@ ------------------------------ update ------------------------------ #
        if append:
            self.data_line_x = np.append(self.data_line_x, line_x)
            self.data_line_y = np.append(self.data_line_y, line_y)
        else:
            self.data_line_x[-1] = line_x
            self.data_line_y[-1] = line_y

        self.plot_line.setData(self.data_line_x,self.data_line_y)   #* setData *#

        self.autorng.x_givenx(x_data= self.data_line_x)            #% autorange %#
        self.autorng.y_givenx(x_data=self.data_line_x, y_datas=[self.data_line_y])

        self.leadhair.slot_data_updated(self.data_line_y[-1])       #% leadhair %#
        self.axix_right.slot_data_updated(self.data_line_y[-1])

    def initial_data(self, line_x, line_y, window:int=None):
        #@ ------------------------------ initial ----------------------------- #
        self.update_data(line_x, line_y, append=True)
        self.autorng.x_minmax(line_x, window)

    def slot_mouse_moved(self, evt):
        # ---------------------------- slot_mouse ---------------------------- #
        self.crosshair.slot_mouse_moved(evt)                      #% crosshair %#
        self.axix_left.slot_mouse_moved(evt)

    def slot_range_changed(self):
        # ---------------------------- slot_range ---------------------------- #
        self.crosshair.slot_range_changed()                       #% crosshair %#
        self.autorng.y_givenx(x_data=self.data_line_x, y_datas=[self.data_line_y])

class CrossHair:
    def __init__(self, viewbox:pg.ViewBox):
        self.vb = viewbox
        self.data_scene_pos = pg.QtCore.QPointF(0,0)

        pen = pg.mkPen(color="#cccccc", style=QtCore.Qt.DashLine, width=0.6)
        self.vline = pg.InfiniteLine(angle=90, movable=False,pen=pen)
        self.hline = pg.InfiniteLine(angle=0, movable=False,pen=pen)
        
        self.vb.addItem(self.vline, ignoreBounds=False)
        self.vb.addItem(self.hline, ignoreBounds=False)

    def slot_mouse_moved(self, pos):
        self.data_scene_pos = pos
        self.update_position()

    def slot_range_changed(self):
        self.update_position()

    def update_position(self):
        mouse_view_pos = self.vb.mapSceneToView(self.data_scene_pos)
        self.vline.setPos(mouse_view_pos.x()) ## round(mouse_view_pos.x())
        self.hline.setPos(mouse_view_pos.y()) ## round(mouse_view_pos.x())

class LeadHair:
    def __init__(self, viewbox:pg.ViewBox):
        self.vb = viewbox
        self.mouse_view_y = 0

        pen = pg.mkPen(color="#a8d0ab", style=QtCore.Qt.SolidLine, width=0.6)
        self.hline = pg.InfiniteLine(angle=0, movable=False,pen=pen)
        self.vb.addItem(self.hline, ignoreBounds=False)

    def slot_data_updated(self, new_y):
        self.mouse_view_y = new_y
        self.update_position()

    def update_position(self):
        self.hline.setPos(self.mouse_view_y) ## round(mouse_view_pos.x())

class AutoRange:
    def __init__(self, viewbox:pg.ViewBox):
        self.vb = viewbox

    def x_limits(self, x_data):
        self.vb.setLimits(xMin= min(x_data)-100, xMax=max(x_data)+100, minXRange=20)

    def x_minmax(self, x_data, window:int = None):
        # if not self.vb.is_dragging and not self.vb.is_wheeling:
        if self.vb.is_autorange:
            x_end = max(x_data) 
            x_sta = min(x_data) if window is None else x_end - window  
            self.vb.setXRange(x_sta, x_end, padding=0.05)

    def x_window(self, x_data):
        # if not self.vb.is_dragging and not self.vb.is_wheeling:
        if self.vb.is_autorange:
            x_min, x_max = self.vb.viewRange()[0]
            window = x_max - x_min
            threshold = window * 0.05 
            x_data_max =  max(x_data)
            self.vb.setXRange(x_data_max - window + threshold, x_data_max + threshold, padding=0.00)

    def x_givenx(self, x_data):
        x_min, x_max = self.vb.viewRange()[0]
        threshold = (x_max-x_min)*0.05
        if x_min <= x_data[-1] <= x_max :
            if x_min <= x_data[0] <= x_max :
                self.x_minmax(x_data)
            else:
                self.x_window(x_data) 
        self.x_limits(x_data)


    def y_givenx(self, x_data, y_datas:list):
            x_min, x_max = self.vb.getViewBox().viewRange()[0]
            y_min, y_max = self.vb.getViewBox().viewRange()[1]
            x_mask = (x_data >= x_min) & (x_data <= x_max)
            if sum(x_mask) > 0:
                y_data_min = np.min([np.min(y_data[x_mask]) for y_data in y_datas])
                y_data_max = np.max([np.max(y_data[x_mask]) for y_data in y_datas])
                if not (y_data_min == y_min and y_data_max == y_max):
                    self.vb.setYRange(y_data_min, y_data_max)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pwg = PlotWidget()
        self.setCentralWidget(self.pwg)
        # ----------------------------- init data ---------------------------- #
        x = np.arange(1000, dtype=float)
        y = np.random.normal(size=1000)+100
        y += 5 * np.sin(x/100) 
        self.pwg.initial_data(x,y)
        # ---------------------------- update data --------------------------- #
        self.test_cnt = 1

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # 500 밀리초마다 업데이트
        self.timer.timeout.connect(self.update)
        self.timer.start()

        
    def update(self):
        #@ ------------------------------- data ------------------------------- #
        x_new = len(self.pwg.data_line_x)
        y_new = np.random.normal(size=1)[0] + 5 * np.sin(x_new/100) +100

        if self.test_cnt %5 == 0:
            self.pwg.update_data(x_new, y_new, append=True)
            self.test_cnt = 1
        else:
            self.pwg.update_data(x_new, y_new, append=False)
            self.test_cnt += 1

        # -------------------------------------------------------------------- #

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MainWindow()

    win.show()
    app.exec()
