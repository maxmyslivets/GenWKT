from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QFileDialog
from PySide6.QtCore import Qt

class CoordsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Секция WGS84
        wgs_card = QFrame()
        wgs_card.setObjectName("card_square")
        wgs_layout = QVBoxLayout(wgs_card)
        wgs_layout.setContentsMargins(15, 15, 15, 15)
        
        wgs_header = QHBoxLayout()
        wgs_title = QLabel("WGS84 (ID, Lat, Lon, H)")
        wgs_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        wgs_header.addWidget(wgs_title)
        wgs_header.addStretch()
        self.btn_load_wgs = QPushButton("Загрузить")
        self.btn_load_wgs.setFixedWidth(100)
        self.btn_load_wgs.clicked.connect(lambda: self.load_file(self.text_wgs))
        wgs_header.addWidget(self.btn_load_wgs)
        wgs_layout.addLayout(wgs_header)
        
        self.text_wgs = QTextEdit()
        self.text_wgs.setPlaceholderText("1,55.9132151,28.7827337,148.13\n...")
        wgs_layout.addWidget(self.text_wgs)
        
        layout.addWidget(wgs_card, 0, 0)
        
        # Секция МСК
        msk_card = QFrame()
        msk_card.setObjectName("card_square")
        msk_layout = QVBoxLayout(msk_card)
        msk_layout.setContentsMargins(15, 15, 15, 15)
        
        msk_header = QHBoxLayout()
        msk_title = QLabel("МСК (ID, x, y, h)")
        msk_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        msk_header.addWidget(msk_title)
        msk_header.addStretch()
        self.btn_load_msk = QPushButton("Загрузить")
        self.btn_load_msk.setFixedWidth(100)
        self.btn_load_msk.clicked.connect(lambda: self.load_file(self.text_msk))
        msk_header.addWidget(self.btn_load_msk)
        msk_layout.addLayout(msk_header)
        
        self.text_msk = QTextEdit()
        self.text_msk.setPlaceholderText("1,7686.0995773235,-8996.72764806,128.313878864\n...")
        msk_layout.addWidget(self.text_msk)
        
        layout.addWidget(msk_card, 0, 1)

    def load_file(self, text_widget):
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_widget.setText(content)
            except Exception as e:
                # В реальном приложении показать диалог ошибки
                print(f"Ошибка загрузки файла: {e}")

    def get_data(self):
        return {
            "wgs": self.text_wgs.toPlainText(),
            "msk": self.text_msk.toPlainText()
        }
