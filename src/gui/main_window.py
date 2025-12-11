from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QStackedWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream
import sys
import os
from src.gui.widgets.projection_widget import ProjectionWidget
from src.gui.widgets.coords_widget import CoordsWidget
from src.gui.widgets.results_widget import ResultsWidget
from src.gui.widgets.wkt_converter_widget import WktConverterWidget
from src.gui.widgets.settings_widget import SettingsWidget
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
        self.resize(1400, 900)
        
        # Установка иконки
        icon_path = self.resource_path("assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Загрузка стилей
        self.load_styles()
        
        # Инициализация логики
        self.converter = CoordinateConverter()
        self.estimator = ParameterEstimator()
        
        self.setup_ui()

        self.setup_ui()

    def load_styles(self):
        # Load theme from config
        theme_name = config.get("app.theme", "Dark")
        self.apply_theme(theme_name)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Sidebar ===
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200) # Narrower sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # App Title in Sidebar
        title_label = QPushButton(f"{config.get('app.name')}")
        title_label.setObjectName("appTitle")
        title_label.setFlat(True)
        title_label.setEnabled(False) # Just for display
        sidebar_layout.addWidget(title_label)

        # Navigation Buttons
        self.btn_nav_calc = QPushButton("Расчет")
        self.btn_nav_calc.setIcon(QIcon(self.resource_path("assets/calc.svg")))
        self.btn_nav_calc.setCheckable(True)
        self.btn_nav_calc.setChecked(True)
        self.btn_nav_calc.clicked.connect(lambda: self.switch_tab(0))
        sidebar_layout.addWidget(self.btn_nav_calc)

        self.btn_nav_wkt = QPushButton("WKT")
        self.btn_nav_wkt.setIcon(QIcon(self.resource_path("assets/wkt.svg")))
        self.btn_nav_wkt.setCheckable(True)
        self.btn_nav_wkt.clicked.connect(lambda: self.switch_tab(1))
        sidebar_layout.addWidget(self.btn_nav_wkt)

        sidebar_layout.addStretch()
        
        # Settings Button
        self.btn_nav_settings = QPushButton("Настройки")
        self.btn_nav_settings.setIcon(QIcon(self.resource_path("assets/settings.svg")))
        self.btn_nav_settings.setCheckable(True)
        self.btn_nav_settings.clicked.connect(lambda: self.switch_tab(2))
        sidebar_layout.addWidget(self.btn_nav_settings)
        
        # Version info
        version_label = QPushButton(f"v{config.get('app.version')}")
        version_label.setObjectName("versionLabel")
        version_label.setFlat(True)
        version_label.setEnabled(False)
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(self.sidebar)

        # === Content Area ===
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)

        # Page 1: Calculation
        self.page_calc = QWidget()
        self.setup_calc_page()
        self.content_area.addWidget(self.page_calc)

        # Page 2: WKT
        self.page_wkt = WktConverterWidget()
        self.content_area.addWidget(self.page_wkt)
        
        # Page 3: Settings
        self.page_settings = SettingsWidget()
        self.page_settings.theme_changed.connect(self.apply_theme)
        self.content_area.addWidget(self.page_settings)
        
        # Group buttons for exclusive checking
        self.nav_group = [self.btn_nav_calc, self.btn_nav_wkt, self.btn_nav_settings]

    def switch_tab(self, index):
        self.content_area.setCurrentIndex(index)
        # Update button states
        for i, btn in enumerate(self.nav_group):
            btn.setChecked(i == index)
            
    def apply_theme(self, theme_name):
        theme_map = {
            "Dark": "dark_theme.qss",
            "Oceanic Blue": "oceanic.qss",
            "Emerald Tech": "emerald.qss",
            "Sunset Pro": "sunset.qss"
        }
        
        filename = theme_map.get(theme_name, "dark_theme.qss")
        style_path = self.resource_path(f"src/gui/styles/{filename}")
        
        style_file = QFile(style_path)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
            style_file.close()
            logger.info(f"Применена тема: {theme_name}")
            # Save to config
            # config.set("app.theme", theme_name)
        else:
            logger.warning(f"Не удалось загрузить стили QSS: {style_path}")

    def setup_calc_page(self):
        # Main Horizontal Layout
        main_layout = QHBoxLayout(self.page_calc)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # === Left Column (Inputs & Controls) ===
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        self.proj_widget = ProjectionWidget()
        left_layout.addWidget(self.proj_widget)
        
        self.coords_widget = CoordsWidget()
        left_layout.addWidget(self.coords_widget)
        
        self.btn_calc = QPushButton("Сформировать WKT")
        self.btn_calc.setFixedHeight(50)
        self.btn_calc.setObjectName("actionButton")
        self.btn_calc.clicked.connect(self.calculate)
        left_layout.addWidget(self.btn_calc)
        
        main_layout.addWidget(left_column, stretch=1)
        
        # === Right Column (Results) ===
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        self.results_widget = ResultsWidget()
        self.results_widget.geoid_toggled.connect(self.on_geoid_toggled)
        self.results_widget.save_clicked.connect(self.on_save_wkt)
        right_layout.addWidget(self.results_widget)
        
        main_layout.addWidget(right_column, stretch=1)

        # Подключение сигнала автоопределения (оставим как вспомогательную функцию)
        # self.proj_widget.auto_detect_clicked.connect(self.auto_detect_projection) # Button removed

    # auto_detect_projection method removed as it is no longer triggered by any button

    def calculate(self):
        try:
            # 1. Получение и парсинг координат
            data = self.coords_widget.get_data()
            wgs_raw = self.parse_text_data(data["wgs"])
            msk_raw = self.parse_text_data(data["msk"])
            
            if len(wgs_raw) != len(msk_raw):
                raise ValueError("Количество точек не совпадает.")
            
            if len(wgs_raw) < 3:
                raise ValueError("Нужно минимум 3 точки.")

            wgs_coords_list = []
            msk_coords_list = []
            ids = []
            
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
                wgs_coords_list.append([w_lat, w_lon, w_h])
                msk_coords_list.append([m_x, m_y, m_h])

            # --- ЭТАП 1: ПРОЕКЦИЯ ---
            if not self.proj_widget.is_custom_projection():
                # Автоматический расчет параметров проекции
                proj_est = self.estimator.estimate_projection_parameters(wgs_coords_list, msk_coords_list, fixed_scale=True)
                # cm_dms = self.converter.format_dms(proj_est["central_meridian"])
                cm_dms = f"{proj_est['central_meridian']:.9f}"
                
                ui_proj_params = {
                    "cm": cm_dms,
                    "scale": proj_est["scale_factor"],
                    "fe": proj_est["false_easting"],
                    "fn": proj_est["false_northing"],
                    "lat0": 0
                }
                self.proj_widget.set_projection_params(ui_proj_params)
            
            # Получаем текущие параметры проекции из UI (автоматические или пользовательские)
            proj_params = self.proj_widget.get_projection_params()
            cm_deg = self.converter.parse_dms(proj_params["cm"])
            
            # --- ЭТАП 2: ТРАНСФОРМАЦИЯ (ГЕЛЬМЕРТ) ---
            
            # Подготовка координат для Гельмерта (WGS Cartesian -> MSK Cartesian)
            wgs_cartesian = []
            msk_cartesian = []
            
            for i in range(len(wgs_coords_list)):
                w_lat, w_lon, w_h = wgs_coords_list[i]
                m_x, m_y, m_h = msk_coords_list[i]
                
                # WGS -> Cartesian
                wx, wy, wz = self.converter.wgs84_to_cartesian(w_lat, w_lon, w_h)
                wgs_cartesian.append([wx, wy, wz])
                
                # MSK -> Cartesian (обратная задача проекции с текущими параметрами)
                mx, my, mz = self.converter.msk_to_cartesian(
                    northing=m_x, easting=m_y, h=m_h, 
                    central_meridian_deg=cm_deg, 
                    false_easting=proj_params["fe"], 
                    false_northing=proj_params["fn"], 
                    scale_factor=proj_params["scale"], 
                    lat_origin=proj_params["lat0"]
                )
                msk_cartesian.append([mx, my, mz])
                
            wgs_cartesian = np.array(wgs_cartesian)
            msk_cartesian = np.array(msk_cartesian)
            
            if not self.proj_widget.is_custom_transformation():
                # Автоматический расчет параметров Гельмерта
                helmert_params = self.estimator.calculate_helmert(wgs_cartesian, msk_cartesian)
                self.proj_widget.set_transformation_params(helmert_params)
            
            # Получаем текущие параметры трансформации из UI
            trans_params = self.proj_widget.get_transformation_params()
            
            # --- ЭТАП 3: ПРОВЕРКА И ВЫВОД ---
            
            # Применяем трансформацию: WGS Cart -> [Helmert] -> Transformed Cart
            transformed_cart = self.estimator.apply_helmert(wgs_cartesian, trans_params)
            
            # Transformed Cart -> MSK (прямая задача проекции)
            comparison_data = []
            for i in range(len(transformed_cart)):
                tx, ty, tz = transformed_cart[i]
                n, e, h = self.converter.cartesian_to_msk(
                    tx, ty, tz, cm_deg, 
                    proj_params["fe"], proj_params["fn"], 
                    proj_params["scale"], proj_params["lat0"]
                )
                
                # Сравнение с исходными MSK
                orig_n, orig_e, orig_h = msk_coords_list[i]
                
                dx = orig_n - n
                dy = orig_e - e
                dh = orig_h - h
                
                comparison_data.append((ids[i], dx, dy, dh))
                
            # Обновление таблицы сравнения
            self.results_widget.set_comparison_data(comparison_data)
            
            # Генерация WKT
            # Объединяем параметры
            full_params = trans_params.copy() # Tx, Ty, Tz, Rx, Ry, Rz, Scale_ppm
            
            # Сохраняем для обновления при переключении геоида
            self.last_calc_result = {
                "params": full_params,
                "cm_deg": cm_deg,
                "fe": proj_params["fe"],
                "fn": proj_params["fn"],
                "scale": proj_params["scale"],
                "lat0": proj_params["lat0"]
            }
            
            self.update_wkt_display()
            
            logger.info("Расчет и формирование WKT выполнены успешно")
            
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
