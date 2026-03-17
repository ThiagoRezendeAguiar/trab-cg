import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from data_structures.scene import Scene

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint")
        self.setMinimumSize(1200, 720)

        self.scene = Scene()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())