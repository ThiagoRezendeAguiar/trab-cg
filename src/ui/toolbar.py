from enum import Enum
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QHBoxLayout, QToolButton, QFrame, QSizePolicy, QButtonGroup
)

from model.primitives import PrimitiveType
from qt_material_icons import MaterialIcon

class LineAlgorithm(Enum):
    DDA = "DDA"
    BRESENHAM = "Bresenham"

TOOLS = [
    (PrimitiveType.POINT, "fiber_manual_record", "Ponto"),
    (PrimitiveType.LINE, "diagonal_line", "Reta"),
    (PrimitiveType.CIRCLE, "circle", "Circunferência"),
    (PrimitiveType.POLYGON, "hexagon", "Polígono"),
]

PALETTE = {
    "bg":             "#ffffff",   
    "btn_idle":       "#f2f2f7",    
    "btn_hover":      "#e5e5ea",    
    "btn_active":     "#007aff",   
    "btn_active_fg":  "#ffffff",    
    "btn_idle_fg":    "#1c1c1e",    
    "border":         "#d1d1d6",   
}

STYLESHEET = f"""
    QFrame#Toolbar {{
        background-color: {PALETTE['bg']};
        border-bottom: 1px solid {PALETTE['border']};
    }}
    QToolButton {{
        background-color: {PALETTE['btn_idle']};
        color: {PALETTE['btn_idle_fg']};
        border: none;
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
    }}
    QToolButton:hover {{
        background-color: {PALETTE['btn_hover']};
        color: #1c1c1e;
    }}
    QToolButton:checked {{
        background-color: {PALETTE['btn_active']};
        color: {PALETTE['btn_active_fg']};
        font-weight: bold;
    }}
    
    /* --- ESTILO DO CONTROLE SEGMENTADO (ALGORITMOS) --- */
    QFrame#AlgContainer {{
        background-color: {PALETTE['btn_idle']};
        border-radius: 12px;
    }}
    QToolButton.alg-btn {{
        background-color: transparent;
        color: {PALETTE['btn_idle_fg']};
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 13px;
    }}
    QToolButton.alg-btn:hover {{
        background-color: #e5e5ea; /* leve hover no inativo */
    }}
    QToolButton.alg-btn:checked {{
        background-color: {PALETTE['bg']}; /* Fundo branco para destacar */
        color: {PALETTE['btn_active']};    /* Texto azul */
        border: 1px solid {PALETTE['border']}; /* Bordinha sutil */
        font-weight: bold;
    }}
"""

class ToolButton(QToolButton):
    def __init__(self, primitive: PrimitiveType, icon_name: str, label: str, shortcut: str = "", parent=None):
        super().__init__(parent)
        self.primitive = primitive
        
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setIcon(MaterialIcon(icon_name))
        self.setIconSize(QSize(22, 22))
        self.setText(f" {label}")
        if shortcut:
            self.setToolTip(f"{label}  [{shortcut}]")


class ToolBar(QFrame):
    tool_changed = Signal(object)
    algorithm_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toolbar")
        self.setStyleSheet(STYLESHEET)
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_button_clicked)

        for primitive, icon_name, label in TOOLS:
            btn = ToolButton(primitive, icon_name, label, self)
            self.button_group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch()

        self.alg_container = QFrame()
        self.alg_container.setObjectName("AlgContainer")
        self.alg_container.setFixedHeight(40)
        
        alg_layout = QHBoxLayout(self.alg_container)
        alg_layout.setContentsMargins(2, 2, 2, 2)
        alg_layout.setSpacing(0)

        self.alg_group = QButtonGroup(self)
        self.alg_group.setExclusive(True)
        self.alg_group.buttonClicked.connect(self._on_algorithm_changed)

        self.btn_dda = QToolButton()
        self.btn_dda.setText("DDA")
        self.btn_dda.setCheckable(True)
        self.btn_dda.setProperty("class", "alg-btn")
        self.btn_dda.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dda.primitive = LineAlgorithm.DDA
        
        self.btn_bresenham = QToolButton()
        self.btn_bresenham.setText("Bresenham")
        self.btn_bresenham.setCheckable(True)
        self.btn_bresenham.setProperty("class", "alg-btn")
        self.btn_bresenham.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bresenham.primitive = LineAlgorithm.BRESENHAM

        self.alg_group.addButton(self.btn_dda)
        self.alg_group.addButton(self.btn_bresenham)
        alg_layout.addWidget(self.btn_dda)
        alg_layout.addWidget(self.btn_bresenham)

        layout.addWidget(self.alg_container)

        
        if self.button_group.buttons():
            self.button_group.buttons()[1].setChecked(True)
            self._active_tool = self.button_group.buttons()[1].primitive
            
        self.btn_dda.setChecked(True)
        self._active_algorithm = LineAlgorithm.DDA

        self._update_algorithm_visibility()

    @property
    def active_tool(self):
        return self._active_tool

    @property
    def active_algorithm(self):
        return self._active_algorithm

    def _on_button_clicked(self, button: QToolButton):
        self._active_tool = button.primitive
        self.tool_changed.emit(self._active_tool)
        self._update_algorithm_visibility()

    def _on_algorithm_changed(self, button: QToolButton):
        self._active_algorithm = button.primitive
        self.algorithm_changed.emit(self._active_algorithm)

    def _update_algorithm_visibility(self):
        is_line_tool = (self._active_tool == PrimitiveType.LINE)
        self.alg_container.setVisible(is_line_tool)