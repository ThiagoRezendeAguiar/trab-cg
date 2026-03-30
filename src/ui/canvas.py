from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QImage, QPainter, Qt, QPen, QBrush
from PySide6.QtCore import QRect

from algorithms.clipping import cohen_sutherland, liang_barsky
from algorithms.rasterization import circle_bresenham, dda, line_bresenham
from algorithms.transformation import apply_transformations
from model.primitives import Point, Primitive, PrimitiveType
from ui.toolbar import LineAlgorithm

class CanvasWidget(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.current_tool = PrimitiveType.LINE
        self.current_algorithm = LineAlgorithm.DDA
        self.current_clip_algorithm = "CS"
        self.current_radius = 50
        self.temp_points = []
        self.selection_rect = None
        self.clip_rect = None
        
        self._pixelmap = QImage(1920, 1080, QImage.Format_ARGB32)
        self._pixelmap.fill(Qt.white)

    def set_tool(self, tool):
        self.current_tool = tool
        self.temp_points.clear()
        for prim in self.scene.primitives:
            prim.selected = False
        self.update()

    def set_algorithm(self, algo):
        if isinstance(algo, LineAlgorithm):
            self.current_algorithm = algo
        elif algo in ["CS", "LB"]:
            self.current_clip_algorithm = algo
        self.update()

    def set_radius(self, rad): 
        self.current_radius = rad

    def mousePressEvent(self, event):
        if self.current_tool in ("SELECT", "CLIP"):
            if event.button() == Qt.LeftButton:
                self.origin = event.position().toPoint()
                if self.current_tool == "SELECT":
                    self.selection_rect = (self.origin, self.origin)
                    for prim in self.scene.primitives:
                        prim.selected = False
                else:
                    self.clip_rect = (self.origin, self.origin)
            elif event.button() == Qt.RightButton:
                if self.current_tool == "CLIP":
                    self.clip_rect = None
                else:
                    self.selection_rect = None
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
        if self.current_tool == "SELECT" and self.selection_rect:
            self.selection_rect = (self.origin, event.position().toPoint())
            self.update()
        elif self.current_tool == "CLIP" and self.clip_rect:
            self.clip_rect = (self.origin, event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.current_tool == "SELECT" and self.selection_rect:
            self._process_selection() 
            self.selection_rect = None
            self.update()
        elif self.current_tool == "CLIP" and self.clip_rect:
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

        if self.current_tool == "SELECT" and self.selection_rect:
            self._draw_dashed_rect(painter, self.selection_rect, QColor(0, 120, 215))

        if self.clip_rect:
            self._draw_dashed_rect(painter, self.clip_rect, QColor(40, 167, 69))

        if self.temp_points:
            pen = QPen(QColor(255, 120, 0)) 
            painter.setPen(pen)
            brush = QBrush(QColor(255, 120, 0))
            painter.setBrush(brush)
            
            for pt in self.temp_points:
                painter.drawEllipse(pt.x - 3, pt.y - 3, 6, 6)
            
            if len(self.temp_points) > 1 and self.current_tool in (PrimitiveType.POLYGON, PrimitiveType.LINE):
                pen_line = QPen(QColor(255, 120, 0))
                pen_line.setStyle(Qt.DashLine)
                pen_line.setWidth(1)
                painter.setPen(pen_line)
                
                for i in range(len(self.temp_points) - 1):
                    p1 = self.temp_points[i]
                    p2 = self.temp_points[i+1]
                    painter.drawLine(p1.x, p1.y, p2.x, p2.y)

    def _draw_dashed_rect(self, painter, rect_points, color):
        p1, p2 = rect_points
        rect = QRect(p1, p2)
        pen = QPen(color)
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        painter.setPen(pen)
        brush = QBrush(QColor(color.red(), color.green(), color.blue(), 30))
        painter.setBrush(brush)
        painter.drawRect(rect.normalized())

    def _draw_primitive(self, prim):
        draw_color = (255, 0, 0) if prim.selected else prim.color
        points_to_draw = []
        alg = dda if prim.algorithm == LineAlgorithm.DDA else line_bresenham

        def get_clipped_segment(p1, p2):
            if not self.clip_rect:
                return p1, p2
            
            cp1, cp2 = self.clip_rect
            xmin, xmax = min(cp1.x(), cp2.x()), max(cp1.x(), cp2.x())
            ymin, ymax = min(cp1.y(), cp2.y()), max(cp1.y(), cp2.y())
            
            if self.current_clip_algorithm == "CS":
                return cohen_sutherland(p1.x, p1.y, p2.x, p2.y, xmin, ymin, xmax, ymax)
            else:
                return liang_barsky(p1.x, p1.y, p2.x, p2.y, xmin, ymin, xmax, ymax)

        if prim.type == PrimitiveType.LINE:
            seg = get_clipped_segment(prim.p[0], prim.p[1])
            if seg: 
                points_to_draw.extend(alg(seg[0].x, seg[0].y, seg[1].x, seg[1].y))

        elif prim.type == PrimitiveType.POLYGON:
            n = len(prim.p)
            for i in range(n):
                seg = get_clipped_segment(prim.p[i], prim.p[(i + 1) % n])
                if seg:
                    points_to_draw.extend(alg(seg[0].x, seg[0].y, seg[1].x, seg[1].y))

        elif prim.type == PrimitiveType.CIRCLE:
            pts = circle_bresenham(prim.p[0].x, prim.p[0].y, prim.radius)
            if self.clip_rect:
                cp1, cp2 = self.clip_rect
                xmin, xmax = min(cp1.x(), cp2.x()), max(cp1.x(), cp2.x())
                ymin, ymax = min(cp1.y(), cp2.y()), max(cp1.y(), cp2.y())
                points_to_draw.extend([pt for pt in pts if xmin <= pt[0] <= xmax and ymin <= pt[1] <= ymax])
            else:
                points_to_draw.extend(pts)

        elif prim.type == PrimitiveType.POINT:
            pt = prim.p[0]
            if self.clip_rect:
                cp1, cp2 = self.clip_rect
                xmin, xmax = min(cp1.x(), cp2.x()), max(cp1.x(), cp2.x())
                ymin, ymax = min(cp1.y(), cp2.y()), max(cp1.y(), cp2.y())
                if xmin <= pt.x <= xmax and ymin <= pt.y <= ymax:
                    points_to_draw.append((pt.x, pt.y))
            else:
                points_to_draw.append((pt.x, pt.y))

        for x, y in points_to_draw:
            if 0 <= x < self._pixelmap.width() and 0 <= y < self._pixelmap.height():
                self._pixelmap.setPixelColor(x, y, QColor(*draw_color))

    def apply_transformations(self, transforms):
        has_selection = False
        for prim in self.scene.primitives:
            if prim.selected:
                has_selection = True
                apply_transformations(prim, transforms)
        
        if has_selection:
            self.update()