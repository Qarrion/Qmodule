import sys
from PySide6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np

class CrosshairPlot(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Add a plot to the widget
        self.data = np.random.normal(size=100)  # Sample data
        self.plot = self.plot_widget.plot(self.data)

        # Create vertical line for crosshair
        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.plot_widget.addItem(self.v_line, ignoreBounds=True)

        # Create a label for displaying the x-value
        self.x_label = pg.TextItem(anchor=(0,1), color='red')
        self.plot_widget.addItem(self.x_label)

        # Connect the mouse move event to a function
        self.plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)

    def mouse_moved(self, evt):
        # Get the position of the mouse in the plot
        pos = evt
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)

            # Find nearest x-axis tick
            x_ticks = self.plot_widget.getAxis('bottom').tickValues(mouse_point.x(), mouse_point.x())[0][0]
            nearest_tick = min(x_ticks, key=lambda tick: abs(tick[0] - mouse_point.x()))

            # Update the position of the line and x-value label
            self.v_line.setPos(nearest_tick[0])
            self.x_label.setPos(nearest_tick[0], self.plot_widget.plotItem.vb.viewRange()[1][0])
            self.x_label.setText(f'x: {nearest_tick[0]:.2f}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CrosshairPlot()
    main.show()
    sys.exit(app.exec())
