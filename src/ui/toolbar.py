from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QHBoxLayout, QToolButton, QFrame, QButtonGroup, 
    QSpinBox, QDoubleSpinBox, QLabel, QVBoxLayout
)
from model.primitives import PrimitiveType
from qt_material_icons import MaterialIcon
from enum import Enum

class LineAlgorithm(Enum):
    DDA = "DDA"
    BRESENHAM = "Bresenham"

PALETTE = {
    "bg": "#F8F9FA",
    "hover": "#E2E6EA",
    "active": "#0D6EFD",
    "border": "#DEE2E6",
    "text_sec": "#6C757D",
    "text_main": "#212529"
}

STYLESHEET = f"""
    QFrame#Toolbar {{ 
        background-color: {PALETTE['bg']}; 
        border-bottom: 1px solid {PALETTE['border']}; 
    }}
    QToolButton {{
        border: 1px solid transparent;
        border-radius: 6px;
        background: transparent;
        padding: 6px;
        color: {PALETTE['text_main']};
    }}
    QToolButton:hover {{ 
        background-color: {PALETTE['hover']}; 
        border: 1px solid {PALETTE['border']};
    }}
    QToolButton:checked {{ 
        background-color: {PALETTE['active']}; 
        color: white; 
        border: 1px solid {PALETTE['active']};
    }}
    QSpinBox, QDoubleSpinBox {{
        border: 1px solid {PALETTE['border']};
        border-radius: 4px;
        background: white;
        padding: 2px 4px;
        color: {PALETTE['text_main']};
    }}
    QLabel {{ 
        color: {PALETTE['text_sec']}; 
        font-size: 11px; 
        font-weight: 600; 
        text-transform: uppercase; 
    }}
    QLabel.SectionTitle {{
        margin-bottom: 4px;
    }}
"""

class ToolBar(QFrame):
    tool_changed = Signal(object)
    algorithm_changed = Signal(object)
    radius_changed = Signal(int)
    transform_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toolbar")
        self.setStyleSheet(STYLESHEET)
        
        self.setMinimumHeight(80)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 12, 20, 12) 
        self.main_layout.setSpacing(30) 

        self._init_draw_section()
        self._add_separator()
        self._init_algorithm_section()
        self._add_separator()
        self._init_transform_section()
        
        self.main_layout.addStretch()

    def _create_section_container(self, title):
        container = QVBoxLayout()
        container.setSpacing(4)
        lbl = QLabel(title)
        lbl.setProperty("class", "SectionTitle")
        container.addWidget(lbl, alignment=Qt.AlignCenter)
        
        layout = QHBoxLayout()
        layout.setSpacing(4)
        container.addLayout(layout)
        return container, layout

    def _add_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"color: {PALETTE['border']};")
        self.main_layout.addWidget(line)

    def _init_draw_section(self):
        container, layout = self._create_section_container("Ferramentas")
        self.button_group = QButtonGroup(self)
        
        tools = [
            ("SELECT", "select"),
            (PrimitiveType.POINT, "fiber_manual_record"),
            (PrimitiveType.LINE, "diagonal_line"),
            (PrimitiveType.CIRCLE, "circle"),
            (PrimitiveType.POLYGON, "hexagon")
        ]

        for prim, icon in tools:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setIcon(MaterialIcon(icon))
            btn.setIconSize(QSize(22, 22))
            btn.primitive = prim
            self.button_group.addButton(btn)
            layout.addWidget(btn)

        layout.addSpacing(10)
        layout.addWidget(QLabel("R:"))
        
        self.spin_radius = QSpinBox()
        self.spin_radius.setRange(1, 999)
        self.spin_radius.setValue(50)
        self.spin_radius.setFixedWidth(55)
        self.spin_radius.valueChanged.connect(self.radius_changed.emit)
        layout.addWidget(self.spin_radius)
        
        self.main_layout.addLayout(container)
        self.button_group.buttonClicked.connect(lambda b: self.tool_changed.emit(b.primitive))

    def _init_algorithm_section(self):
        container, layout = self._create_section_container("Rasterização")
        self.alg_group = QButtonGroup(self)
        
        for name, alg in [("DDA", LineAlgorithm.DDA), ("BRES", LineAlgorithm.BRESENHAM)]:
            btn = QToolButton()
            btn.setText(name)
            btn.setCheckable(True)
            btn.primitive = alg
            if name == "DDA": btn.setChecked(True)
            self.alg_group.addButton(btn)
            layout.addWidget(btn)
            
        self.main_layout.addLayout(container)
        self.alg_group.buttonClicked.connect(lambda b: self.algorithm_changed.emit(b.primitive))

    def _init_transform_section(self):
        container, layout = self._create_section_container("Transformações")
        layout.setSpacing(6)

        self.chk_t = QCheckBox("T:")
        self.t_x = QSpinBox(); self.t_y = QSpinBox()
        for s in [self.t_x, self.t_y]: 
            s.setRange(-999, 999)
            s.setFixedWidth(55)
        layout.addWidget(self.chk_t)
        layout.addWidget(self.t_x)
        layout.addWidget(self.t_y)
        layout.addSpacing(10)

        self.chk_s = QCheckBox("S:")
        self.s_x = QDoubleSpinBox(); self.s_y = QDoubleSpinBox()
        for s in [self.s_x, self.s_y]: 
            s.setRange(0, 999)
            s.setValue(1)
            s.setFixedWidth(55)
        layout.addWidget(self.chk_s)
        layout.addWidget(self.s_x)
        layout.addWidget(self.s_y)
        layout.addSpacing(10)

        self.chk_r = QCheckBox("R:")
        self.r_ang = QDoubleSpinBox()
        self.r_ang.setRange(-360, 360)
        self.r_ang.setFixedWidth(55)
        layout.addWidget(self.chk_r)
        layout.addWidget(self.r_ang)
        layout.addSpacing(10)

        self.chk_ref = QCheckBox("Ref:")
        self.ref_cb = QComboBox()
        self.ref_cb.addItems(["X", "Y", "XY"])
        self.ref_cb.setFixedWidth(50)
        layout.addWidget(self.chk_ref)
        layout.addWidget(self.ref_cb)
        layout.addSpacing(10)

        btn_apply = QToolButton()
        btn_apply.setText("Aplicar")
        btn_apply.setStyleSheet(f"background-color: {PALETTE['active']}; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self._emit_multiple_transforms)
        layout.addWidget(btn_apply)

        self.main_layout.addLayout(container)

    def _emit_multiple_transforms(self):
        transforms = {}
        
        if self.chk_t.isChecked():
            transforms['translate'] = (self.t_x.value(), self.t_y.value())
            
        if self.chk_s.isChecked():
            transforms['scale'] = (self.s_x.value(), self.s_y.value())
            
        if self.chk_r.isChecked():
            transforms['rotate'] = self.r_ang.value()
            
        if self.chk_ref.isChecked():
            transforms['reflect'] = self.ref_cb.currentText()
            
        if transforms:
            self.transform_requested.emit(transforms)