from PySide6.QtWidgets import QWidget

class CanvasWidget(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.setMinimumSize(850, 650)