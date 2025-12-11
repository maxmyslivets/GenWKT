from PySide6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, QLineEdit, 
                               QFrame, QPushButton, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt
from src.config.loader import config

class ProjectionWidget(QWidget):
    # auto_detect_clicked signal removed as button is removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_defaults()
        
        # Initial state
        self.toggle_projection_inputs(self.chk_custom_proj.isChecked())
        self.toggle_transformation_inputs(self.chk_custom_trans.isChecked())

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card Frame
        card = QFrame()
        card.setObjectName("card_square")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("Параметры МСК")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        card_layout.addWidget(title)
        
        # === Group 1: Projection Parameters ===
        self.group_proj = QGroupBox("Параметры проекции")
        self.group_proj.setStyleSheet("QGroupBox { font-weight: bold; color: #E0E0E0; border: 1px solid #404040; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_proj = QVBoxLayout(self.group_proj)
        
        self.chk_custom_proj = QCheckBox("Использовать пользовательские параметры")
        self.chk_custom_proj.setToolTip("Если включено, параметры не будут рассчитываться автоматически")
        self.chk_custom_proj.toggled.connect(self.toggle_projection_inputs)
        layout_proj.addWidget(self.chk_custom_proj)
        
        grid_proj = QGridLayout()
        grid_proj.setSpacing(10)
        
        grid_proj.addWidget(QLabel("Lon0:"), 0, 0)
        self.entry_cm = QLineEdit()
        self.entry_cm.setPlaceholderText("29.0000000")
        grid_proj.addWidget(self.entry_cm, 0, 1)
        
        grid_proj.addWidget(QLabel("Масштаб (Scale):"), 0, 2)
        self.entry_scale = QLineEdit()
        self.entry_scale.setPlaceholderText("1.0")
        grid_proj.addWidget(self.entry_scale, 0, 3)
        
        grid_proj.addWidget(QLabel("False Easting (м):"), 1, 0)
        self.entry_fe = QLineEdit()
        self.entry_fe.setPlaceholderText("500000")
        grid_proj.addWidget(self.entry_fe, 1, 1)
        
        grid_proj.addWidget(QLabel("False Northing (м):"), 1, 2)
        self.entry_fn = QLineEdit()
        self.entry_fn.setPlaceholderText("0")
        grid_proj.addWidget(self.entry_fn, 1, 3)
        
        grid_proj.addWidget(QLabel("Широта начала (Lat0):"), 2, 0)
        self.entry_lat0 = QLineEdit()
        self.entry_lat0.setPlaceholderText("0")
        grid_proj.addWidget(self.entry_lat0, 2, 1)
        
        # Button removed per user request

        layout_proj.addLayout(grid_proj)
        card_layout.addWidget(self.group_proj)
        
        # === Group 2: Transformation Parameters ===
        self.group_trans = QGroupBox("Параметры трансформации (Гельмерт)")
        self.group_trans.setStyleSheet("QGroupBox { font-weight: bold; color: #E0E0E0; border: 1px solid #404040; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_trans = QVBoxLayout(self.group_trans)
        
        self.chk_custom_trans = QCheckBox("Использовать пользовательские параметры")
        self.chk_custom_trans.setToolTip("Если включено, параметры не будут рассчитываться автоматически")
        self.chk_custom_trans.toggled.connect(self.toggle_transformation_inputs)
        layout_trans.addWidget(self.chk_custom_trans)
        
        grid_trans = QGridLayout()
        grid_trans.setSpacing(10)
        
        # Tx, Ty, Tz
        grid_trans.addWidget(QLabel("Tx (м):"), 0, 0)
        self.entry_tx = QLineEdit()
        self.entry_tx.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_tx, 0, 1)
        
        grid_trans.addWidget(QLabel("Ty (м):"), 0, 2)
        self.entry_ty = QLineEdit()
        self.entry_ty.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_ty, 0, 3)
        
        grid_trans.addWidget(QLabel("Tz (м):"), 1, 0)
        self.entry_tz = QLineEdit()
        self.entry_tz.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_tz, 1, 1)
        
        # Rx, Ry, Rz
        grid_trans.addWidget(QLabel("Rx (сек):"), 1, 2)
        self.entry_rx = QLineEdit()
        self.entry_rx.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_rx, 1, 3)
        
        grid_trans.addWidget(QLabel("Ry (сек):"), 2, 0)
        self.entry_ry = QLineEdit()
        self.entry_ry.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_ry, 2, 1)
        
        grid_trans.addWidget(QLabel("Rz (сек):"), 2, 2)
        self.entry_rz = QLineEdit()
        self.entry_rz.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_rz, 2, 3)
        
        # Scale
        grid_trans.addWidget(QLabel("Scale (ppm):"), 3, 0)
        self.entry_s = QLineEdit()
        self.entry_s.setPlaceholderText("0.0")
        grid_trans.addWidget(self.entry_s, 3, 1)
        
        layout_trans.addLayout(grid_trans)
        card_layout.addWidget(self.group_trans)
        
        layout.addWidget(card)

        # Подключение сигналов для замены запятой на точку
        self.entries_proj = [self.entry_cm, self.entry_scale, self.entry_fe, self.entry_fn, self.entry_lat0]
        self.entries_trans = [self.entry_tx, self.entry_ty, self.entry_tz, self.entry_rx, self.entry_ry, self.entry_rz, self.entry_s]
        
        for entry in self.entries_proj + self.entries_trans:
            entry.setMinimumWidth(120)
            entry.textChanged.connect(lambda text, e=entry: self.on_text_changed(text, e))

    def on_text_changed(self, text, entry):
        if ',' in text:
            cursor_pos = entry.cursorPosition()
            entry.setText(text.replace(',', '.'))
            entry.setCursorPosition(cursor_pos)

    def toggle_projection_inputs(self, checked):
        for entry in self.entries_proj:
            entry.setReadOnly(not checked)
            # Optional: Change style to indicate disabled state visually if needed, 
            # but QLineEdit usually handles this.
            # We can also use setEnabled(checked) but setReadOnly allows copying.
            # Let's use setEnabled for clearer visual cue as requested "block input".
            entry.setEnabled(checked)

    def toggle_transformation_inputs(self, checked):
        for entry in self.entries_trans:
            entry.setEnabled(checked)

    def load_defaults(self):
        self.entry_cm.setText(config.get("projection.central_meridian", ""))
        self.entry_scale.setText(str(config.get("projection.scale_factor", "")))
        self.entry_fe.setText(str(config.get("projection.false_easting", "")))
        self.entry_fn.setText(str(config.get("projection.false_northing", "")))
        self.entry_lat0.setText(str(config.get("projection.lat_origin", "")))
        
        # Defaults for transformation (usually 0)
        for entry in self.entries_trans:
            entry.clear()

    def get_projection_params(self):
        return {
            "cm": self.entry_cm.text(),
            "scale": float(self.entry_scale.text() or 1.0),
            "fe": float(self.entry_fe.text() or 0.0),
            "fn": float(self.entry_fn.text() or 0.0),
            "lat0": float(self.entry_lat0.text() or 0.0)
        }

    def set_projection_params(self, params):
        if "cm" in params:
            self.entry_cm.setText(str(params["cm"]))
        if "scale" in params:
            self.entry_scale.setText(str(params["scale"]))
        if "fe" in params:
            self.entry_fe.setText(f"{params['fe']:.4f}")
        if "fn" in params:
            self.entry_fn.setText(f"{params['fn']:.4f}")
        if "lat0" in params:
            self.entry_lat0.setText(str(params["lat0"]))

    def get_transformation_params(self):
        return {
            "Tx": float(self.entry_tx.text() or 0.0),
            "Ty": float(self.entry_ty.text() or 0.0),
            "Tz": float(self.entry_tz.text() or 0.0),
            "Rx": float(self.entry_rx.text() or 0.0),
            "Ry": float(self.entry_ry.text() or 0.0),
            "Rz": float(self.entry_rz.text() or 0.0),
            "Scale_ppm": float(self.entry_s.text() or 0.0)
        }

    def set_transformation_params(self, params):
        if "Tx" in params: self.entry_tx.setText(f"{params['Tx']:.4f}")
        if "Ty" in params: self.entry_ty.setText(f"{params['Ty']:.4f}")
        if "Tz" in params: self.entry_tz.setText(f"{params['Tz']:.4f}")
        if "Rx" in params: self.entry_rx.setText(f"{params['Rx']:.5f}")
        if "Ry" in params: self.entry_ry.setText(f"{params['Ry']:.5f}")
        if "Rz" in params: self.entry_rz.setText(f"{params['Rz']:.5f}")
        if "Scale_ppm" in params: self.entry_s.setText(f"{params['Scale_ppm']:.5f}")

    def is_custom_projection(self):
        return self.chk_custom_proj.isChecked()

    def is_custom_transformation(self):
        return self.chk_custom_trans.isChecked()
