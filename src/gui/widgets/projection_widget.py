from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QLineEdit, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal
from src.config.loader import config

class ProjectionWidget(QWidget):
    auto_detect_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_defaults()

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
        title = QLabel("Параметры проекции МСК")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        card_layout.addWidget(title)
        
        # Grid for inputs
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Row 0
        grid.addWidget(QLabel("Осевой меридиан (ГГ ММ СС,сс):"), 0, 0)
        self.entry_cm = QLineEdit()
        self.entry_cm.setPlaceholderText("29 59 59,91779")
        grid.addWidget(self.entry_cm, 0, 1)
        
        grid.addWidget(QLabel("Масштаб (Scale):"), 0, 2)
        self.entry_scale = QLineEdit()
        self.entry_scale.setPlaceholderText("1.0")
        grid.addWidget(self.entry_scale, 0, 3)
        
        # Row 1
        grid.addWidget(QLabel("False Easting (м):"), 1, 0)
        self.entry_fe = QLineEdit()
        self.entry_fe.setPlaceholderText("500000")
        grid.addWidget(self.entry_fe, 1, 1)
        
        grid.addWidget(QLabel("False Northing (м):"), 1, 2)
        self.entry_fn = QLineEdit()
        self.entry_fn.setPlaceholderText("0")
        grid.addWidget(self.entry_fn, 1, 3)
        
        # Row 2
        grid.addWidget(QLabel("Широта начала (Lat0):"), 2, 0)
        self.entry_lat0 = QLineEdit()
        self.entry_lat0.setPlaceholderText("0")
        grid.addWidget(self.entry_lat0, 2, 1)
        
        # Row 3 - Кнопка автоопределения
        self.btn_auto = QPushButton("Авто-определение")
        self.btn_auto.setToolTip("Автоматически определить параметры проекции по введенным координатам")
        self.btn_auto.clicked.connect(self.auto_detect_clicked.emit)
        grid.addWidget(self.btn_auto, 2, 3)
        
        card_layout.addLayout(grid)
        layout.addWidget(card)

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

    def set_params(self, params):
        """
        Установка параметров в поля ввода.
        params: dict с ключами cm, scale, fe, fn, lat0
        """
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
