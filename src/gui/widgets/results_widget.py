from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                               QFrame, QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit)
from PySide6.QtCore import Signal, Qt

class ResultsWidget(QWidget):
    geoid_toggled = Signal(bool)
    crs_name_changed = Signal(str)
    save_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Верхняя часть: Сравнение координат (теперь занимает больше места, т.к. параметры ушли в инпуты)
        card_comp = QFrame()
        card_comp.setObjectName("card")
        comp_layout = QVBoxLayout(card_comp)
        comp_layout.setContentsMargins(15, 15, 15, 15)
        
        title_comp = QLabel("Сравнение координат (Исходные vs Рассчитанные)")
        title_comp.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        comp_layout.addWidget(title_comp)
        
        self.table_comp = QTableWidget()
        self.table_comp.setColumnCount(4)
        self.table_comp.setHorizontalHeaderLabels(["ID", "dX (м)", "dY (м)", "dH (м)"])
        self.table_comp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_comp.verticalHeader().setVisible(False)
        comp_layout.addWidget(self.table_comp)
        
        layout.addWidget(card_comp)
        
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
        
        controls_layout.addWidget(QLabel("Имя СК:"))
        from PySide6.QtWidgets import QLineEdit
        self.entry_crs_name = QLineEdit()
        self.entry_crs_name.setPlaceholderText("unknown")
        self.entry_crs_name.setFixedWidth(150)
        self.entry_crs_name.textChanged.connect(self.crs_name_changed.emit)
        controls_layout.addWidget(self.entry_crs_name)
        
        self.chk_geoid = QCheckBox("Использовать геоид (EGM2008)")
        self.chk_geoid.toggled.connect(self.geoid_toggled.emit)
        controls_layout.addWidget(self.chk_geoid)
        
        controls_layout.addStretch()
        
        self.btn_save = QPushButton("Сохранить в .prj")
        self.btn_save.clicked.connect(self.save_clicked.emit)
        controls_layout.addWidget(self.btn_save)
        
        wkt_layout.addLayout(controls_layout)
        
        layout.addWidget(card_wkt)

    def set_comparison_data(self, data):
        """
        Заполнение таблицы сравнения.
        data: список кортежей (id, dx, dy, dh)
        """
        self.table_comp.setRowCount(len(data))
        for i, (pt_id, dx, dy, dh) in enumerate(data):
            self.table_comp.setItem(i, 0, QTableWidgetItem(str(pt_id)))
            self.table_comp.setItem(i, 1, QTableWidgetItem(f"{dx:.4f}"))
            self.table_comp.setItem(i, 2, QTableWidgetItem(f"{dy:.4f}"))
            self.table_comp.setItem(i, 3, QTableWidgetItem(f"{dh:.4f}"))

    def set_wkt_text(self, text):
        self.text_wkt.setText(text)
