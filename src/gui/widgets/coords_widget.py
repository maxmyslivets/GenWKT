from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QTextEdit, QPushButton, QGroupBox, QFileDialog
from PySide6.QtCore import Qt

class CoordsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        
        # Секция WGS84
        wgs_group = QGroupBox("WGS84 (ID, Lat, Lon, H)")
        wgs_layout = QGridLayout(wgs_group)
        
        self.btn_load_wgs = QPushButton("Загрузить из файла")
        self.btn_load_wgs.clicked.connect(lambda: self.load_file(self.text_wgs))
        wgs_layout.addWidget(self.btn_load_wgs, 0, 0)
        
        self.text_wgs = QTextEdit()
        self.text_wgs.setPlaceholderText("1,55.9132151,28.7827337,148.13\n...")
        wgs_layout.addWidget(self.text_wgs, 1, 0)
        
        layout.addWidget(wgs_group, 0, 0)
        
        # Секция МСК
        msk_group = QGroupBox("МСК (ID, x, y, h)")
        msk_layout = QGridLayout(msk_group)
        
        self.btn_load_msk = QPushButton("Загрузить из файла")
        self.btn_load_msk.clicked.connect(lambda: self.load_file(self.text_msk))
        msk_layout.addWidget(self.btn_load_msk, 0, 0)
        
        self.text_msk = QTextEdit()
        self.text_msk.setPlaceholderText("1,7686.0995773235,-8996.72764806,128.313878864\n...")
        msk_layout.addWidget(self.text_msk, 1, 0)
        
        layout.addWidget(msk_group, 0, 1)

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
