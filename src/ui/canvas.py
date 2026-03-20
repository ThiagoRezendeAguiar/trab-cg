from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QImage, QPainter, Qt, QPen, QBrush
from PySide6.QtCore import QRect

from algorithms.rasterization import circle_bresenham, dda, line_bresenham
from model.primitives import Point, Primitive, PrimitiveType
from ui.toolbar import LineAlgorithm

class CanvasWidget(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.current_tool = PrimitiveType.LINE
        self.current_algorithm = LineAlgorithm.DDA
        self.current_radius = 50
        self.temp_points = []
        self.selection_rect = None
        
        self._pixelmap = QImage(1920, 1080, QImage.Format_ARGB32)
        self._pixelmap.fill(Qt.white)

    def set_tool(self, tool):
        self.current_tool = tool
        self.temp_points.clear()
        for prim in self.scene.primitives:
            prim.selected = False
        self.update()

    def set_algorithm(self, algo): 
        self.current_algorithm = algo

    def set_radius(self, rad): 
        self.current_radius = rad

    def mousePressEvent(self, event):
        if self.current_tool == "SELECT":
            if event.button() == Qt.LeftButton:
                self.origin = event.position().toPoint()
                self.selection_rect = (self.origin, self.origin)

                for prim in self.scene.primitives:
                    prim.selected = False

                self.update()
            return

        p = Point(int(event.position().x()), int(event.position().y()))
        
        if event.button() == Qt.LeftButton:
            self.temp_points.append(p)
            needed = {
                PrimitiveType.POINT: 1, 
                PrimitiveType.CIRCLE: 1, 
                PrimitiveType.LINE: 2,
                PrimitiveType.POLYGON: -1
            }
            limit = needed.get(self.current_tool, 0)
            if limit > 0 and len(self.temp_points) == limit:
                self._finish_primitive()
        elif event.button() == Qt.RightButton:
            if self.current_tool == PrimitiveType.POLYGON and len(self.temp_points) >= 3:
                self._finish_primitive()
            else:
                self.temp_points.clear()
        self.update()
    
    def mouseMoveEvent(self, event):
        if self.current_tool == "SELECT" and hasattr(self, 'selection_rect') and self.selection_rect:
            self.selection_rect = (self.origin, event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.current_tool == "SELECT" and hasattr(self, 'selection_rect') and self.selection_rect:
            self._process_selection() 
            self.selection_rect = None
            self.update()

    def _process_selection(self):
        p1, p2 = self.selection_rect
        x_min, x_max = min(p1.x(), p2.x()), max(p1.x(), p2.x())
        y_min, y_max = min(p1.y(), p2.y()), max(p1.y(), p2.y())

        for prim in self.scene.primitives:
            prim.selected = any(
                x_min <= pt.x <= x_max and y_min <= pt.y <= y_max 
                for pt in prim.p
            )

    def _finish_primitive(self):
        primitive = Primitive(type=self.current_tool, p=list(self.temp_points))
        
        if self.current_tool in (PrimitiveType.LINE, PrimitiveType.POLYGON):
            primitive.algorithm = self.current_algorithm
        if self.current_tool == PrimitiveType.CIRCLE:
            primitive.radius = self.current_radius

        self.scene.add_primitive(primitive)
        self.temp_points.clear()   

    def paintEvent(self, event):
        self._pixelmap.fill(Qt.white)
        
        for prim in self.scene.primitives:
            self._draw_primitive(prim)
            
        painter = QPainter(self)
        painter.drawImage(0, 0, self._pixelmap)

        if self.current_tool == "SELECT" and hasattr(self, 'selection_rect') and self.selection_rect:
            p1, p2 = self.selection_rect
            rect = QRect(p1, p2)
            
            pen = QPen(QColor(0, 120, 215))
            pen.setStyle(Qt.DashLine)
            pen.setWidth(1)
            painter.setPen(pen)
            
            brush = QBrush(QColor(0, 120, 215, 50))
            painter.setBrush(brush)

            painter.drawRect(rect.normalized())

    def _draw_primitive(self, prim):
        
        def calc_polygon_points(p):
            points = []
            alg = dda if p.algorithm == LineAlgorithm.DDA else line_bresenham
            n = len(p.p)
            
            for i in range(n):
                p1 = p.p[i]
                p2 = p.p[(i + 1) % n]
                points.extend(alg(p1.x, p1.y, p2.x, p2.y))
            return points
       
        handlers = {
            PrimitiveType.POINT: lambda p: [(p.p[0].x, p.p[0].y)],
            PrimitiveType.LINE: lambda p: (dda if p.algorithm == LineAlgorithm.DDA else line_bresenham)(p.p[0].x, p.p[0].y, p.p[1].x, p.p[1].y),
            PrimitiveType.CIRCLE: lambda p: circle_bresenham(p.p[0].x, p.p[0].y, p.radius),
            PrimitiveType.POLYGON: calc_polygon_points
        }

        calc_points = handlers.get(prim.type)
        if calc_points:
            draw_color = (255, 0, 0) if prim.selected else prim.color
            for x, y in calc_points(prim):
                self._pixelmap.setPixelColor(x, y, QColor(*draw_color))