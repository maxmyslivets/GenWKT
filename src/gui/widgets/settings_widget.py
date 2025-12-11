from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QFrame, QGridLayout
from PySide6.QtCore import Signal
from src.config.loader import config

class SettingsWidget(QWidget):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card Frame
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Title
        title = QLabel("Настройки приложения")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        card_layout.addWidget(title)

        # Grid for settings
        grid = QGridLayout()
        grid.setSpacing(15)

        # Theme Selection
        grid.addWidget(QLabel("Цветовая тема:"), 0, 0)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Dark", "Oceanic Blue", "Emerald Tech", "Sunset Pro"])
        self.combo_theme.currentTextChanged.connect(self.on_theme_changed)
        grid.addWidget(self.combo_theme, 0, 1)

        card_layout.addLayout(grid)
        card_layout.addStretch()
        
        layout.addWidget(card)
        layout.addStretch()

    def load_settings(self):
        current_theme = config.get("app.theme", "Dark")
        self.combo_theme.setCurrentText(current_theme)

    def on_theme_changed(self, theme_name):
        self.theme_changed.emit(theme_name)
        config.set("app.theme", theme_name) 
