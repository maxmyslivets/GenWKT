from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QGroupBox, QCheckBox, QPushButton
from PySide6.QtCore import Signal

class ResultsWidget(QWidget):
    geoid_toggled = Signal(bool)
    save_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Верхняя часть: Параметры и Сравнение
        top_layout = QHBoxLayout()
        
        # Группа 1: Рассчитанные параметры
        group_params = QGroupBox("Рассчитанные параметры")
        params_layout = QVBoxLayout(group_params)
        self.text_params = QTextEdit()
        self.text_params.setReadOnly(True)
        self.text_params.setFontFamily("Consolas")
        params_layout.addWidget(self.text_params)
        top_layout.addWidget(group_params)
        
        # Группа 2: Сравнение координат
        group_comp = QGroupBox("Сравнение координат")
        comp_layout = QVBoxLayout(group_comp)
        self.text_comp = QTextEdit()
        self.text_comp.setReadOnly(True)
        self.text_comp.setFontFamily("Consolas")
        self.text_comp.setLineWrapMode(QTextEdit.NoWrap) # Чтобы таблица не ломалась
        comp_layout.addWidget(self.text_comp)
        top_layout.addWidget(group_comp)
        
        layout.addLayout(top_layout)
        
        # Нижняя часть: WKT
        group_wkt = QGroupBox("WKT (для GIS)")
        wkt_layout = QVBoxLayout(group_wkt)
        
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
        
        layout.addWidget(group_wkt)

    def set_params_text(self, text):
        self.text_params.setText(text)

    def set_comparison_text(self, text):
        self.text_comp.setText(text)

    def set_wkt_text(self, text):
        self.text_wkt.setText(text)
