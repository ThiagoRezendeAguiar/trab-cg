from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QColor, QImage, QPainter, Qt
from PySide6.QtCore import QTimer

from algorithms.rasterization import dda, line_bresenham
from model.primitives import Point, Primitive, PrimitiveType
from ui.toolbar import LineAlgorithm

class CanvasWidget(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene

        self.current_tool = PrimitiveType.LINE
        self.current_algorithm = LineAlgorithm.DDA
        self.temp_points = []
    
        screen = QApplication.primaryScreen().size()
        self._pixelmap = QImage(screen.width(), screen.height(), QImage.Format_ARGB32)
        self._pixelmap.fill(Qt.white)

    def set_tool(self, tool):
        self.current_tool = tool
        self.temp_points.clear()

    def set_algorithm(self, algorithm):
        self.current_algorithm = algorithm

    def mousePressEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())
        
        if event.button() == Qt.LeftButton:
            self.temp_points.append(Point(x, y))
            if self.current_tool == PrimitiveType.POINT:
                self._finish_primitive() 
            elif self.current_tool in (PrimitiveType.LINE, PrimitiveType.CIRCLE):
                if len(self.temp_points) == 2:
                    self._finish_primitive()    
            elif self.current_tool == PrimitiveType.POLYGON:
                pass    
        elif event.button() == Qt.RightButton:
            if self.current_tool == PrimitiveType.POLYGON and len(self.temp_points) >= 3:
                self._finish_primitive()
            else:
                self.temp_points.clear()
                
        self.update()

    def _finish_primitive(self):
        primitive = Primitive(
            type=self.current_tool,
            p=list(self.temp_points)
        )

        if self.current_tool == PrimitiveType.LINE:
            primitive.algorithm = self.current_algorithm

        self.scene.add_primitive(primitive)
        self.temp_points.clear()

    def put_pixel(self, x: int, y:int , color):
        if 0 <= x < self._pixelmap.width() and 0 <= y < self._pixelmap.height():
            self._pixelmap.setPixelColor(x, y, QColor(*color))

    def paintEvent(self, event):
        self._pixelmap.fill(Qt.white)
        for primitive in self.scene.primitives:
            self._draw_primitive(primitive)
        painter = QPainter(self)
        painter.drawImage(0, 0, self._pixelmap)

    def _draw_primitive(self, primitive):
        if primitive.type == PrimitiveType.POINT:
            self.put_pixel(primitive.p[0].x, primitive.p[0].y, primitive.color)
        
        elif primitive.type == PrimitiveType.LINE:
            if primitive.algorithm == LineAlgorithm.DDA:
                points = dda(
                   primitive.p[0].x, primitive.p[0].y,
                   primitive.p[1].x, primitive.p[1].y
                )
            elif primitive.algorithm == LineAlgorithm.BRESENHAM:
                 points = line_bresenham(
                   primitive.p[0].x, primitive.p[0].y,
                   primitive.p[1].x, primitive.p[1].y
                )
            
            for x, y in points:
                self.put_pixel(x, y, primitive.color)

        elif primitive.type == PrimitiveType.CIRCLE:
            pass

    def force_redraw(self):
        self.update()