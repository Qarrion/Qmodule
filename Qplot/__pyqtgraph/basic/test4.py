import pyqtgraph as pg
from PySide6.QtWidgets import QApplication

class CustomAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(CustomAxis, self).__init__(*args, **kwargs)
        self.customTicks = [(10, "특별한 값")]

    def tickStrings(self, values, scale, spacing):
        strings = super(CustomAxis, self).tickStrings(values, scale, spacing)
        for val, s in self.customTicks:
            if val in values:
                idx = values.index(val)
                strings[idx] = s
        return strings

    def tickValues(self, minVal, maxVal, size):
        values = super(CustomAxis, self).tickValues(minVal, maxVal, size)
        for level, ticks in self.customTicks:
            if minVal <= level <= maxVal:
                values[-1][1].append(level)
        return values

app = QApplication([])
plot_widget = pg.PlotWidget(axisItems={'bottom': CustomAxis(orientation='bottom')})
plot_widget.plot([1, 2, 3, 4, 5, 10], [1, 2, 3, 4, 5, 6])  # 예시 데이터
plot_widget.show()
app.exec()
