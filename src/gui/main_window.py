from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream
import sys
import os
from src.gui.widgets.projection_widget import ProjectionWidget
from src.gui.widgets.coords_widget import CoordsWidget
from src.gui.widgets.results_widget import ResultsWidget
from src.gui.widgets.wkt_converter_widget import WktConverterWidget
from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator
from src.core.logger import logger
from src.config.loader import config
import numpy as np

class MainWindow(QMainWindow):
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.get('app.name')} v{config.get('app.version')}")
        self.resize(1200, 900)
        
        # Установка иконки
        icon_path = self.resource_path("assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Загрузка стилей
        self.load_styles()
        
        # Инициализация логики
        self.converter = CoordinateConverter()
        self.estimator = ParameterEstimator()
        
        self.setup_ui()

    def load_styles(self):
        style_path = self.resource_path("src/gui/styles/dark_theme.qss")
        style_file = QFile(style_path)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
            style_file.close()
        else:
            logger.warning(f"Не удалось загрузить стили QSS: {style_path}")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Вкладка 1: Расчет
        self.tab_calc = QWidget()
        self.setup_calc_tab()
        self.tabs.addTab(self.tab_calc, "Расчет параметров")
        
        # Вкладка 2: WKT
        self.tab_wkt = WktConverterWidget()
        self.tabs.addTab(self.tab_wkt, "Конвертер по WKT")

    def setup_calc_tab(self):
        layout = QVBoxLayout(self.tab_calc)
        
        self.proj_widget = ProjectionWidget()
        layout.addWidget(self.proj_widget)
        
        self.coords_widget = CoordsWidget()
        layout.addWidget(self.coords_widget)
        
        self.btn_calc = QPushButton("РАССЧИТАТЬ ПАРАМЕТРЫ")
        self.btn_calc.setFixedHeight(50)
        self.btn_calc.clicked.connect(self.calculate)
        layout.addWidget(self.btn_calc)
        
        self.results_widget = ResultsWidget()
        self.results_widget.geoid_toggled.connect(self.on_geoid_toggled)
        self.results_widget.save_clicked.connect(self.on_save_wkt)
        layout.addWidget(self.results_widget)

        # Подключение сигнала автоопределения
        self.proj_widget.auto_detect_clicked.connect(self.auto_detect_projection)

    def auto_detect_projection(self):
        try:
            # 1. Получение координат
            data = self.coords_widget.get_data()
            wgs_raw = self.parse_text_data(data["wgs"])
            msk_raw = self.parse_text_data(data["msk"])
            
            if len(wgs_raw) != len(msk_raw):
                raise ValueError("Количество точек WGS и МСК не совпадает.")
            
            if len(wgs_raw) < 3:
                raise ValueError("Нужно минимум 3 точки для определения параметров.")
                
            wgs_coords = []
            msk_coords = []
            
            for i in range(len(wgs_raw)):
                # WGS: [ID, Lat, Lon, H]
                w_lat = float(wgs_raw[i][1])
                w_lon = float(wgs_raw[i][2])
                w_h = float(wgs_raw[i][3])
                wgs_coords.append([w_lat, w_lon, w_h])
                
                # MSK: [ID, X, Y, H]
                m_x = float(msk_raw[i][1])
                m_y = float(msk_raw[i][2])
                m_h = float(msk_raw[i][3])
                msk_coords.append([m_x, m_y, m_h])
                
            # 2. Оценка параметров
            # Используем fixed_scale=True, так как для МСК масштаб обычно 1.0
            params = self.estimator.estimate_projection_parameters(wgs_coords, msk_coords, fixed_scale=True)
            
            # 3. Обновление UI
            cm_dms = self.converter.format_dms(params["central_meridian"])
            
            ui_params = {
                "cm": cm_dms,
                "scale": params["scale_factor"],
                "fe": params["false_easting"],
                "fn": params["false_northing"],
                "lat0": 0 # Обычно 0
            }
            
            self.proj_widget.set_params(ui_params)
            
            QMessageBox.information(self, "Успех", 
                                    f"Параметры успешно определены:\n"
                                    f"CM: {cm_dms}\n"
                                    f"FE: {params['false_easting']:.3f}\n"
                                    f"FN: {params['false_northing']:.3f}")
            
            logger.info(f"Автоопределение параметров успешно: {params}")
            
        except Exception as e:
            logger.exception("Ошибка автоопределения параметров")
            QMessageBox.warning(self, "Ошибка", f"Не удалось определить параметры:\n{e}")

    def calculate(self):
        try:
            # 1. Получение параметров проекции
            proj_params = self.proj_widget.get_params()
            cm_deg = self.converter.parse_dms(proj_params["cm"])
            
            # 2. Получение координат
            data = self.coords_widget.get_data()
            wgs_raw = self.parse_text_data(data["wgs"])
            msk_raw = self.parse_text_data(data["msk"])
            
            if len(wgs_raw) != len(msk_raw):
                raise ValueError("Количество точек не совпадает.")
            
            if len(wgs_raw) < 3:
                raise ValueError("Нужно минимум 3 точки.")
                
            # 3. Конвертация и Оценка
            wgs_coords = []
            msk_coords = []
            ids = []
            msk_original = []
            
            for i in range(len(wgs_raw)):
                # WGS
                w_id = wgs_raw[i][0]
                w_lat = float(wgs_raw[i][1])
                w_lon = float(wgs_raw[i][2])
                w_h = float(wgs_raw[i][3])
                
                # MSK
                m_id = msk_raw[i][0]
                m_x = float(msk_raw[i][1])
                m_y = float(msk_raw[i][2])
                m_h = float(msk_raw[i][3])
                
                ids.append(w_id)
                msk_original.append([m_x, m_y, m_h])
                
                # WGS -> Декартовы
                wx, wy, wz = self.converter.wgs84_to_cartesian(w_lat, w_lon, w_h)
                wgs_coords.append([wx, wy, wz])
                
                # МСК -> Декартовы
                mx, my, mz = self.converter.msk_to_cartesian(
                    northing=m_x, easting=m_y, h=m_h, 
                    central_meridian_deg=cm_deg, 
                    false_easting=proj_params["fe"], 
                    false_northing=proj_params["fn"], 
                    scale_factor=proj_params["scale"], 
                    lat_origin=proj_params["lat0"]
                )
                msk_coords.append([mx, my, mz])
                
            wgs_coords = np.array(wgs_coords)
            msk_coords = np.array(msk_coords)
            
            # Оценка
            params = self.estimator.calculate_helmert(wgs_coords, msk_coords)
            
            # Проверка
            transformed_cart = self.estimator.apply_helmert(wgs_coords, params)
            
            # Сравнение
            msk_calculated = []
            for i in range(len(transformed_cart)):
                tx, ty, tz = transformed_cart[i]
                n, e, h = self.converter.cartesian_to_msk(
                    tx, ty, tz, cm_deg, 
                    proj_params["fe"], proj_params["fn"], 
                    proj_params["scale"], proj_params["lat0"]
                )
                msk_calculated.append([n, e, h])
                
            # --- Формирование вывода ---
            
            # 1. Параметры
            res_params = f"=== Параметры проекции ===\n"
            res_params += f"CM (deg): {cm_deg:.9f}\n\n"
            
            res_params += "=== Рассчитанные параметры (WGS84 -> МСК) ===\n"
            res_params += f"Tx: {params['Tx']:.4f} м\n"
            res_params += f"Ty: {params['Ty']:.4f} м\n"
            res_params += f"Tz: {params['Tz']:.4f} м\n"
            res_params += f"Rx: {params['Rx']:.5f} сек\n"
            res_params += f"Ry: {params['Ry']:.5f} сек\n"
            res_params += f"Rz: {params['Rz']:.5f} сек\n"
            res_params += f"Scale: {params['Scale_ppm']:.5f} ppm\n"
            
            self.results_widget.set_params_text(res_params)
            
            # 2. Сравнение
            res_comp = f"{'ID':<5} | {'dX':<8} | {'dY':<8} | {'dH':<8}\n"
            res_comp += "-"*40 + "\n"
            
            for i in range(len(ids)):
                orig = msk_original[i]
                calc = msk_calculated[i]
                
                dx = orig[0] - calc[0]
                dy = orig[1] - calc[1]
                dh = orig[2] - calc[2]
                
                res_comp += f"{ids[i]:<5} | {dx:<8.4f} | {dy:<8.4f} | {dh:<8.4f}\n"
                
            self.results_widget.set_comparison_text(res_comp)
            
            # 3. WKT
            # Сохраняем данные для перегенерации WKT
            self.last_calc_result = {
                "params": params,
                "cm_deg": cm_deg,
                "fe": proj_params["fe"],
                "fn": proj_params["fn"],
                "scale": proj_params["scale"],
                "lat0": proj_params["lat0"]
            }
            
            self.update_wkt_display()
            
            logger.info("Расчет выполнен успешно")
            
        except Exception as e:
            logger.exception("Ошибка расчета")
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_wkt_display(self):
        if not hasattr(self, 'last_calc_result'):
            return
            
        use_geoid = self.results_widget.chk_geoid.isChecked()
        data = self.last_calc_result
        
        wkt = self.estimator.generate_wkt(
            data["params"], data["cm_deg"], data["fe"], data["fn"], 
            data["scale"], data["lat0"], use_geoid=use_geoid
        )
        self.results_widget.set_wkt_text(wkt)

    def on_geoid_toggled(self, checked):
        self.update_wkt_display()

    def on_save_wkt(self):
        from PySide6.QtWidgets import QFileDialog
        wkt_text = self.results_widget.text_wkt.toPlainText()
        if not wkt_text:
            QMessageBox.warning(self, "Внимание", "Нет данных WKT для сохранения")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить WKT", "", "Projection Files (*.prj);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(wkt_text)
                QMessageBox.information(self, "Успех", "Файл сохранен")
            except Exception as e:
                logger.exception("Ошибка сохранения файла")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def parse_text_data(self, text):
        import re
        data = []
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = re.split(r'[,\t]', line)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 4:
                data.append(parts[:4])
        return data
