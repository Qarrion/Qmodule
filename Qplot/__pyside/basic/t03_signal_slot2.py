from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

class Communicator(QObject):
    custom_signal = Signal(int, str)

class Receiver(QObject):
    @Slot(int, str)
    def on_custom_signal(self, value, message):
        print(f"Received value: {value}, message: {message}")

app = QApplication([])

communicator = Communicator()
receiver = Receiver()

communicator.custom_signal.connect(receiver.on_custom_signal)

# 시그널 emit
communicator.custom_signal.emit(42, "Hello, World!")

app.exec()