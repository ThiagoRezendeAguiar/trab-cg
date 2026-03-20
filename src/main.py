import sys
import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from model.scene import Scene
from ui.canvas import CanvasWidget
from ui.toolbar import ToolBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint")
        self.setMinimumSize(1200, 720)
            
        self.scene = Scene()
        self.canvas = CanvasWidget(self.scene)
        self.toolbar = ToolBar()

        central = QWidget()
        self.setCentralWidget(central)

        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        
        v.addWidget(self.toolbar)
        
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(20, 20, 20, 20)
        canvas_layout.addWidget(self.canvas)
        
        v.addWidget(canvas_container, stretch=1)

        self.toolbar.tool_changed.connect(self.canvas.set_tool)
        self.toolbar.algorithm_changed.connect(self.canvas.set_algorithm)
        self.toolbar.radius_changed.connect(self.canvas.set_radius)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())