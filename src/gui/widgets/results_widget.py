from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame, QCheckBox, QPushButton
from PySide6.QtCore import Signal

class ResultsWidget(QWidget):
    geoid_toggled = Signal(bool)
    save_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Верхняя часть: Параметры и Сравнение
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        # Группа 1: Рассчитанные параметры
        card_params = QFrame()
        card_params.setObjectName("card")
        params_layout = QVBoxLayout(card_params)
        params_layout.setContentsMargins(15, 15, 15, 15)
        
        title_params = QLabel("Рассчитанные параметры")
        title_params.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        params_layout.addWidget(title_params)
        
        self.text_params = QTextEdit()
        self.text_params.setReadOnly(True)
        self.text_params.setFontFamily("Consolas")
        params_layout.addWidget(self.text_params)
        top_layout.addWidget(card_params)
        
        # Группа 2: Сравнение координат
        card_comp = QFrame()
        card_comp.setObjectName("card")
        comp_layout = QVBoxLayout(card_comp)
        comp_layout.setContentsMargins(15, 15, 15, 15)
        
        title_comp = QLabel("Сравнение координат")
        title_comp.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        comp_layout.addWidget(title_comp)
        
        self.text_comp = QTextEdit()
        self.text_comp.setReadOnly(True)
        self.text_comp.setFontFamily("Consolas")
        self.text_comp.setLineWrapMode(QTextEdit.NoWrap)
        comp_layout.addWidget(self.text_comp)
        top_layout.addWidget(card_comp)
        
        layout.addLayout(top_layout)
        
        # Нижняя часть: WKT
        card_wkt = QFrame()
        card_wkt.setObjectName("card")
        wkt_layout = QVBoxLayout(card_wkt)
        wkt_layout.setContentsMargins(15, 15, 15, 15)
        
        title_wkt = QLabel("WKT (для GIS)")
        title_wkt.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        wkt_layout.addWidget(title_wkt)
        
        self.text_wkt = QTextEdit()
        self.text_wkt.setReadOnly(True)
        self.text_wkt.setFontFamily("Consolas")
        wkt_layout.addWidget(self.text_wkt)
        
        # Панель управления WKT
        controls_layout = QHBoxLayout()
        self.chk_geoid = QCheckBox("Использовать геоид (EGM2008)")
        self.chk_geoid.toggled.connect(self.geoid_toggled.emit)
        controls_layout.addWidget(self.chk_geoid)
        
        controls_layout.addStretch()
        
        self.btn_save = QPushButton("Сохранить в .prj")
        self.btn_save.clicked.connect(self.save_clicked.emit)
        controls_layout.addWidget(self.btn_save)
        
        wkt_layout.addLayout(controls_layout)
        
        layout.addWidget(card_wkt)

    def set_params_text(self, text):
        self.text_params.setText(text)

    def set_comparison_text(self, text):
        self.text_comp.setText(text)

    def set_wkt_text(self, text):
        self.text_wkt.setText(text)
