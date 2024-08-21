# """
# Demonstrates the usage of DateAxisItem to display properly-formatted 
# timestamps on x-axis which automatically adapt to current zoom level.

# """

# import time

# import numpy as np

# import pyqtgraph as pg

# app = pg.mkQApp("DateAxisItem Example")

# # Create a plot with a date-time axis
# w = pg.PlotWidget(axisItems = {'bottom': pg.DateAxisItem()})
# w.showGrid(x=True, y=True)

# # Plot sin(1/x^2) with timestamps in the last 100 years
# now = time.time()
# x = np.linspace(2*np.pi, 1000*2*np.pi, 8301)
# w.plot(now-(2*np.pi/x)**2*100*np.pi*1e7, np.sin(x), symbol='o')

# w.setWindowTitle('pyqtgraph example: DateAxisItem')
# w.show()

# if __name__ == '__main__':
#     pg.exec()

import sys
import numpy as np
import datetime as dt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pyqtgraph import PlotWidget, DateAxisItem, mkPen

class CustomDateAxisItem(DateAxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = '%Y-%m-%d %H:%M'  # Default format

    def tickStrings(self, values, scale, spacing):
        return [dt.datetime.fromtimestamp(value).strftime(self.format) for value in values]

    def setFormat(self, fmt):
        self.format = fmt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PySide6 with pyqtgraph Example")
        self.setGeometry(100, 100, 800, 600)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.setCentralWidget(widget)
        
        # Create a CustomDateAxisItem with custom formatting
        self.date_axis = CustomDateAxisItem(orientation='bottom')
        
        self.plot_widget = PlotWidget(axisItems={'bottom': self.date_axis})
        layout.addWidget(self.plot_widget)
        
        self.plot_data()

    def plot_data(self):
        # Generate sample data
        now = dt.datetime.now()
        timestamps = [now - dt.timedelta(minutes=i * 10) for i in range(60)]  # 10 minute intervals
        dates = [dt.datetime.timestamp(ts) for ts in timestamps]
        values = np.random.rand(60) * 10
        
        self.plot_widget.plot(x=dates, y=values, pen=mkPen(color='b', width=2))
        
        self.update_axis_format()
        self.plot_widget.showGrid(x=True, y=True)

    def update_axis_format(self):
        x_range = self.plot_widget.getPlotItem().viewRange()[0]
        duration_seconds = x_range[1] - x_range[0]
        
        if duration_seconds < 3600:  # less than 1 hour
            self.date_axis.setFormat('%H:%M')
        elif duration_seconds < 86400:  # less than 1 day
            self.date_axis.setFormat('%m-%d %H:%M')
        else:
            self.date_axis.setFormat('%Y-%m-%d')

        self.plot_widget.getPlotItem().setXRange(x_range[0], x_range[1])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
