# test_pyqt.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Test")
        self.setGeometry(100, 100, 300, 200)
        button = QPushButton("Test Button", self)
        button.setGeometry(100, 80, 100, 30)

app = QApplication(sys.argv)
window = TestWindow()
window.show()
sys.exit(app.exec())