from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QLineEdit, QFrame, 
                               QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from src.core.converter import CoordinateConverter
from src.core.logger import logger
import csv

class WktConverterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.converter = CoordinateConverter()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 1. Секция ввода WKT
        card_wkt = QFrame()
        card_wkt.setObjectName("card")
        wkt_layout = QVBoxLayout(card_wkt)
        wkt_layout.setContentsMargins(15, 15, 15, 15)
        
        wkt_header = QHBoxLayout()
        wkt_title = QLabel("Параметры WKT")
        wkt_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        wkt_header.addWidget(wkt_title)
        wkt_header.addStretch()
        btn_load_prj = QPushButton("Загрузить из .prj")
        btn_load_prj.clicked.connect(self.load_from_prj)
        wkt_header.addWidget(btn_load_prj)
        wkt_layout.addLayout(wkt_header)
        
        self.wkt_edit = QTextEdit()
        self.wkt_edit.setPlaceholderText('Пример: PROJCS["Transverse_Mercator",GEOGCS["GCS_Pulkovo_1942",DATUM["D_Pulkovo_1942",SPHEROID["Krassowsky_1942",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",39.0],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]')
        wkt_layout.addWidget(self.wkt_edit)
        
        layout.addWidget(card_wkt)
        
        # 2. Секция ввода координат (WGS84)
        card_input = QFrame()
        card_input.setObjectName("card")
        input_layout = QVBoxLayout(card_input)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        input_header = QHBoxLayout()
        input_title = QLabel("Координаты WGS84 (ID, Lat, Lon, H)")
        input_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        input_header.addWidget(input_title)
        input_header.addStretch()
        btn_load_file = QPushButton("Загрузить из файла")
        btn_load_file.clicked.connect(self.load_coords_from_file)
        input_header.addWidget(btn_load_file)
        input_layout.addLayout(input_header)
        
        self.coords_input = QTextEdit()
        self.coords_input.setPlaceholderText("Введите координаты построчно (разделитель запятая или пробел):\n1,54.9183617,28.7378755,145\n2,54.8922442,28.7457653,147\n3,54.8688434,28.7250955,171")
        input_layout.addWidget(self.coords_input)
        
        # Лейбл предупреждения о высоте
        self.lbl_height_warning = QLabel("Высоты не пересчитывались, т.к. в WKT не описана вертикальная система координат")
        self.lbl_height_warning.setStyleSheet("color: #FF5555; font-weight: bold;")
        self.lbl_height_warning.setWordWrap(True)
        self.lbl_height_warning.setVisible(False)
        input_layout.addWidget(self.lbl_height_warning)
        
        layout.addWidget(card_input)
        
        # 3. Кнопка действия
        self.btn_convert = QPushButton("КОНВЕРТИРОВАТЬ")
        self.btn_convert.setFixedHeight(40)
        self.btn_convert.setObjectName("actionButton")
        self.btn_convert.clicked.connect(self.convert)
        layout.addWidget(self.btn_convert)
        
        # 4. Секция результатов (МСК)
        card_result = QFrame()
        card_result.setObjectName("card")
        result_layout = QVBoxLayout(card_result)
        result_layout.setContentsMargins(15, 15, 15, 15)
        
        result_header = QHBoxLayout()
        result_title = QLabel("Результат (МСК)")
        result_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        result_header.addWidget(result_title)
        result_header.addStretch()
        btn_save_file = QPushButton("Сохранить в файл")
        btn_save_file.clicked.connect(self.save_results_to_file)
        result_header.addWidget(btn_save_file)
        result_layout.addLayout(result_header)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["ID", "X (Север)", "Y (Восток)", "H (Высота)"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setStyleSheet("background-color: #2D2D2D; border: 1px solid #404040; color: #E0E0E0; gridline-color: #404040;")
        self.result_table.verticalHeader().setVisible(False)
        result_layout.addWidget(self.result_table)
        
        layout.addWidget(card_result)
        
    def load_from_prj(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл PRJ", "", "Projection Files (*.prj);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    wkt_text = f.read()
                    self.wkt_edit.setText(wkt_text)
                logger.info(f"Загружен WKT из {file_name}")
            except Exception as e:
                logger.exception(f"Не удалось загрузить файл PRJ: {file_name}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

    def load_coords_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл координат", "", "Text Files (*.txt *.csv);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.coords_input.setText(text)
                logger.info(f"Загружены координаты из {file_name}")
            except Exception as e:
                logger.exception(f"Не удалось загрузить файл координат: {file_name}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

    def save_results_to_file(self):
        if self.result_table.rowCount() == 0:
            QMessageBox.warning(self, "Внимание", "Нет результатов для сохранения")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить результаты", "", "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Заголовки
                    headers = [self.result_table.horizontalHeaderItem(i).text() for i in range(self.result_table.columnCount())]
                    writer.writerow(headers)
                    
                    # Данные
                    for row in range(self.result_table.rowCount()):
                        row_data = []
                        for col in range(self.result_table.columnCount()):
                            item = self.result_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                logger.info(f"Результаты сохранены в {file_name}")
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен:\n{file_name}")
            except Exception as e:
                logger.exception(f"Не удалось сохранить файл: {file_name}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def convert(self):
        try:
            wkt = self.wkt_edit.toPlainText().strip()
            if not wkt:
                raise ValueError("Введите WKT строку.")
            
            # Проверка наличия вертикальной CRS для отображения предупреждения
            has_vertical = self.converter.check_vertical_crs(wkt)
            self.lbl_height_warning.setVisible(not has_vertical)
            
            input_text = self.coords_input.toPlainText().strip()
            if not input_text:
                raise ValueError("Введите координаты.")
            
            lines = input_text.split('\n')
            results = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Замена запятых на точки (кроме тех, что разделяют поля, если это CSV)
                # Но пользователь может использовать запятую как разделитель полей.
                # Поэтому сначала пробуем разделить по запятой.
                
                parts = line.split(',')
                if len(parts) < 2:
                    # Если запятых нет, пробуем пробелы
                    parts = line.split()
                
                # Очистка частей
                parts = [p.strip() for p in parts if p.strip()]
                
                if len(parts) < 2:
                    continue 

                pt_id = ""
                lat = 0.0
                lon = 0.0
                h = 0.0
                
                try:
                    # Логика определения полей:
                    # 4 поля: ID, Lat, Lon, H
                    # 3 поля: Lat, Lon, H (ID пустой)
                    # 2 поля: Lat, Lon (ID пустой, H=0)
                    
                    if len(parts) >= 4:
                        pt_id = parts[0]
                        lat = float(parts[1])
                        lon = float(parts[2])
                        h = float(parts[3])
                    elif len(parts) == 3:
                        # Может быть ID, Lat, Lon ИЛИ Lat, Lon, H
                        # Попробуем распарсить первое как число. Если это ID, оно может быть числом.
                        # Но Lat тоже число.
                        # Предположим стандарт Lat, Lon, H если 3 числа.
                        lat = float(parts[0])
                        lon = float(parts[1])
                        h = float(parts[2])
                    elif len(parts) == 2:
                        lat = float(parts[0])
                        lon = float(parts[1])
                    
                    n, e, h_msk = self.converter.wkt_to_msk(wkt, lat, lon, h)
                    results.append((pt_id, n, e, h_msk))
                    
                except ValueError:
                    # Если не удалось распарсить как числа, возможно первый элемент это ID
                    if len(parts) == 3:
                        try:
                            pt_id = parts[0]
                            lat = float(parts[1])
                            lon = float(parts[2])
                            n, e, h_msk = self.converter.wkt_to_msk(wkt, lat, lon, h)
                            results.append((pt_id, n, e, h_msk))
                        except ValueError:
                            continue
                    else:
                        continue
            
            # Заполнение таблицы
            self.result_table.setRowCount(len(results))
            for i, (pt_id, n, e, h_msk) in enumerate(results):
                self.result_table.setItem(i, 0, QTableWidgetItem(str(pt_id)))
                self.result_table.setItem(i, 1, QTableWidgetItem(f"{n:.4f}"))
                self.result_table.setItem(i, 2, QTableWidgetItem(f"{e:.4f}"))
                self.result_table.setItem(i, 3, QTableWidgetItem(f"{h_msk:.4f}"))
            
            logger.info(f"Конвертировано {len(results)} точек по WKT")
            
        except Exception as e:
            logger.exception("Ошибка конвертации WKT")
            QMessageBox.critical(self, "Ошибка", str(e))
