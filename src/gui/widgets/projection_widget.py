from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QGroupBox
from PySide6.QtCore import Qt
from src.config.loader import config

class ProjectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_defaults()

    def setup_ui(self):
        layout = QGridLayout(self)
        
        group = QGroupBox("Параметры проекции МСК")
        group_layout = QGridLayout(group)
        
        # Row 0
        group_layout.addWidget(QLabel("Осевой меридиан (ГГ ММ СС,сс):"), 0, 0)
        self.entry_cm = QLineEdit()
        self.entry_cm.setPlaceholderText("29 59 59,91779")
        group_layout.addWidget(self.entry_cm, 0, 1)
        
        group_layout.addWidget(QLabel("Масштаб (Scale):"), 0, 2)
        self.entry_scale = QLineEdit()
        self.entry_scale.setPlaceholderText("1.0")
        group_layout.addWidget(self.entry_scale, 0, 3)
        
        # Row 1
        group_layout.addWidget(QLabel("False Easting (м):"), 1, 0)
        self.entry_fe = QLineEdit()
        self.entry_fe.setPlaceholderText("500000")
        group_layout.addWidget(self.entry_fe, 1, 1)
        
        group_layout.addWidget(QLabel("False Northing (м):"), 1, 2)
        self.entry_fn = QLineEdit()
        self.entry_fn.setPlaceholderText("0")
        group_layout.addWidget(self.entry_fn, 1, 3)
        
        # Row 2
        group_layout.addWidget(QLabel("Широта начала (Lat0):"), 2, 0)
        self.entry_lat0 = QLineEdit()
        self.entry_lat0.setPlaceholderText("0")
        group_layout.addWidget(self.entry_lat0, 2, 1)
        
        layout.addWidget(group, 0, 0)

        # Подключение сигналов для замены запятой на точку
        for entry in [self.entry_cm, self.entry_scale, self.entry_fe, self.entry_fn, self.entry_lat0]:
            entry.textChanged.connect(lambda text, e=entry: self.on_text_changed(text, e))

    def on_text_changed(self, text, entry):
        if ',' in text:
            cursor_pos = entry.cursorPosition()
            entry.setText(text.replace(',', '.'))
            entry.setCursorPosition(cursor_pos)

    def load_defaults(self):
        self.entry_cm.setText(config.get("projection.central_meridian", ""))
        self.entry_scale.setText(str(config.get("projection.scale_factor", "")))
        self.entry_fe.setText(str(config.get("projection.false_easting", "")))
        self.entry_fn.setText(str(config.get("projection.false_northing", "")))
        self.entry_lat0.setText(str(config.get("projection.lat_origin", "")))

    def get_params(self):
        return {
            "cm": self.entry_cm.text(),
            "scale": float(self.entry_scale.text() or 1.0),
            "fe": float(self.entry_fe.text() or 0.0),
            "fn": float(self.entry_fn.text() or 0.0),
            "lat0": float(self.entry_lat0.text() or 0.0)
        }
