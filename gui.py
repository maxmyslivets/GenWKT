import customtkinter as ctk
from tkinter import filedialog, messagebox
import numpy as np
import os
import re
from logic import CoordinateConverter, ParameterEstimator

# Установка темы
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("7 Parameter Calculator (WGS84 -> MSK)")
        self.geometry("1200x900")
        
        self.converter = CoordinateConverter()
        self.estimator = ParameterEstimator()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()
        self.load_initial_data()
        
    def setup_ui(self):
        # Создание Tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_calc = self.tabview.add("Расчет параметров")
        self.tab_wkt = self.tabview.add("Конвертер по WKT")
        
        self.setup_calc_tab()
        self.setup_wkt_tab()

    def setup_calc_tab(self):
        parent = self.tab_calc
        parent.grid_columnconfigure(0, weight=1)
        
        # === Параметры проекции ===
        self.proj_frame = ctk.CTkFrame(parent)
        self.proj_frame.grid(row=0, column=0, sticky="ew", pady=10)
        self.proj_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(self.proj_frame, text="Параметры проекции МСК", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Row 1
        ctk.CTkLabel(self.proj_frame, text="Осевой меридиан (ГГ ММ СС,сс):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_cm = ctk.CTkEntry(self.proj_frame, placeholder_text="29 59 59,91779")
        self.entry_cm.grid(row=1, column=1, padx=5, pady=5)
        self.add_context_menu(self.entry_cm)
        
        ctk.CTkLabel(self.proj_frame, text="Масштаб (Scale):").grid(row=1, column=2, padx=5, pady=5)
        self.entry_scale = ctk.CTkEntry(self.proj_frame, placeholder_text="1.0")
        self.entry_scale.grid(row=1, column=3, padx=5, pady=5)
        self.add_context_menu(self.entry_scale)
        
        # Row 2
        ctk.CTkLabel(self.proj_frame, text="False Easting (м):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_fe = ctk.CTkEntry(self.proj_frame, placeholder_text="500000")
        self.entry_fe.grid(row=2, column=1, padx=5, pady=5)
        self.add_context_menu(self.entry_fe)
        
        ctk.CTkLabel(self.proj_frame, text="False Northing (м):").grid(row=2, column=2, padx=5, pady=5)
        self.entry_fn = ctk.CTkEntry(self.proj_frame, placeholder_text="0")
        self.entry_fn.grid(row=2, column=3, padx=5, pady=5)
        self.add_context_menu(self.entry_fn)
        
        # Row 3
        ctk.CTkLabel(self.proj_frame, text="Широта начала (Lat0):").grid(row=3, column=0, padx=5, pady=5)
        self.entry_lat0 = ctk.CTkEntry(self.proj_frame, placeholder_text="0")
        self.entry_lat0.grid(row=3, column=1, padx=5, pady=5)
        self.add_context_menu(self.entry_lat0)
        
        # === Ввод координат ===
        self.coords_frame = ctk.CTkFrame(parent)
        self.coords_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.coords_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Секция WGS84
        self.wgs_frame = ctk.CTkFrame(self.coords_frame)
        self.wgs_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.wgs_frame, text="WGS84 (ID, Lat, Lon, H)", font=("Arial", 14, "bold")).pack(pady=5)
        self.btn_load_wgs = ctk.CTkButton(self.wgs_frame, text="Загрузить из файла", command=lambda: self.load_file(self.text_wgs))
        self.btn_load_wgs.pack(pady=5)
        
        self.text_wgs = ctk.CTkTextbox(self.wgs_frame, height=200)
        self.text_wgs.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_context_menu(self.text_wgs)
        
        # Секция МСК
        self.msk_frame = ctk.CTkFrame(self.coords_frame)
        self.msk_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.msk_frame, text="МСК (ID, x, y, h)", font=("Arial", 14, "bold")).pack(pady=5)
        self.btn_load_msk = ctk.CTkButton(self.msk_frame, text="Загрузить из файла", command=lambda: self.load_file(self.text_msk))
        self.btn_load_msk.pack(pady=5)
        
        self.text_msk = ctk.CTkTextbox(self.msk_frame, height=200)
        self.text_msk.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_context_menu(self.text_msk)
        
        # === Кнопки действий ===
        self.btn_calc = ctk.CTkButton(parent, text="РАССЧИТАТЬ ПАРАМЕТРЫ", height=50, font=("Arial", 16, "bold"), command=self.calculate)
        self.btn_calc.grid(row=2, column=0, pady=20, sticky="ew")
        
        # === Калькулятор контрольной точки ===
        self.control_frame = ctk.CTkFrame(parent)
        self.control_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self.control_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        ctk.CTkLabel(self.control_frame, text="Контроль преобразования (WGS -> МСК)", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=5, pady=5)
        
        self.entry_ctrl_lat = ctk.CTkEntry(self.control_frame, placeholder_text="Lat")
        self.entry_ctrl_lat.grid(row=1, column=0, padx=5)
        self.add_context_menu(self.entry_ctrl_lat)
        
        self.entry_ctrl_lon = ctk.CTkEntry(self.control_frame, placeholder_text="Lon")
        self.entry_ctrl_lon.grid(row=1, column=1, padx=5)
        self.add_context_menu(self.entry_ctrl_lon)
        
        self.entry_ctrl_h = ctk.CTkEntry(self.control_frame, placeholder_text="H")
        self.entry_ctrl_h.grid(row=1, column=2, padx=5)
        self.add_context_menu(self.entry_ctrl_h)
        
        self.btn_ctrl_calc = ctk.CTkButton(self.control_frame, text="Преобразовать", command=self.calculate_control)
        self.btn_ctrl_calc.grid(row=1, column=3, padx=5)
        
        self.lbl_ctrl_res = ctk.CTkLabel(self.control_frame, text="Результат: -")
        self.lbl_ctrl_res.grid(row=1, column=4, padx=5)
        
        # === Результаты ===
        self.results_frame = ctk.CTkFrame(parent)
        self.results_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(self.results_frame, text="Результаты", font=("Arial", 16, "bold")).pack(pady=10)
        self.text_results = ctk.CTkTextbox(self.results_frame, height=300, font=("Consolas", 12))
        self.text_results.pack(fill="both", expand=True, padx=10, pady=10)
        self.add_context_menu(self.text_results)

    def setup_wkt_tab(self):
        parent = self.tab_wkt
        parent.grid_columnconfigure(0, weight=1)
        
        # Ввод WKT
        ctk.CTkLabel(parent, text="WKT Строка (PROJCS...):", font=("Arial", 14, "bold")).pack(pady=5, anchor="w")
        
        self.btn_load_wkt_file = ctk.CTkButton(parent, text="Загрузить WKT из файла", command=lambda: self.load_file(self.text_wkt))
        self.btn_load_wkt_file.pack(pady=5, anchor="w", padx=5)
        
        self.text_wkt = ctk.CTkTextbox(parent, height=150, font=("Consolas", 10))
        self.text_wkt.pack(fill="x", padx=5, pady=5)
        self.add_context_menu(self.text_wkt)
        
        # Ввод координат
        ctk.CTkLabel(parent, text="Координаты WGS84 (ID, Lat, Lon, H):", font=("Arial", 14, "bold")).pack(pady=5, anchor="w")
        self.btn_load_wkt_wgs = ctk.CTkButton(parent, text="Загрузить из файла", command=lambda: self.load_file(self.text_wkt_wgs))
        self.btn_load_wkt_wgs.pack(pady=5, anchor="w", padx=5)
        
        self.text_wkt_wgs = ctk.CTkTextbox(parent, height=200)
        self.text_wkt_wgs.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_context_menu(self.text_wkt_wgs)
        
        # Кнопка конвертации
        self.btn_wkt_convert = ctk.CTkButton(parent, text="КОНВЕРТИРОВАТЬ", height=40, font=("Arial", 14, "bold"), command=self.convert_wkt)
        self.btn_wkt_convert.pack(pady=10, fill="x", padx=5)
        
        # Результаты
        ctk.CTkLabel(parent, text="Результат (МСК):", font=("Arial", 14, "bold")).pack(pady=5, anchor="w")
        self.text_wkt_res = ctk.CTkTextbox(parent, height=200, font=("Consolas", 12))
        self.text_wkt_res.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_context_menu(self.text_wkt_res)

    def convert_wkt(self):
        try:
            wkt_str = self.text_wkt.get("0.0", "end").strip()
            if not wkt_str:
                messagebox.showwarning("Внимание", "Введите WKT строку.")
                return
                
            wgs_raw = self.parse_text_data(self.text_wkt_wgs.get("0.0", "end"))
            if not wgs_raw:
                messagebox.showwarning("Внимание", "Введите координаты.")
                return
                
            res = f"{'ID':<5} | {'X (North)':<15} | {'Y (East)':<15} | {'H':<10}\n"
            res += "-"*60 + "\n"
            
            for row in wgs_raw:
                pid = row[0]
                lat = float(row[1])
                lon = float(row[2])
                h = float(row[3])
                
                n, e, h_msk = self.converter.wkt_to_msk(wkt_str, lat, lon, h)
                res += f"{pid:<5} | {n:<15.4f} | {e:<15.4f} | {h_msk:<10.4f}\n"
                
            self.text_wkt_res.delete("0.0", "end")
            self.text_wkt_res.insert("0.0", res)
            
        except Exception as e:
            self.text_wkt_res.delete("0.0", "end")
            self.text_wkt_res.insert("0.0", f"Ошибка: {str(e)}")

    def add_context_menu(self, widget):
        # Создание стандартного меню tkinter
        import tkinter as tk
        menu = tk.Menu(widget, tearoff=0)
        
        # Вспомогательные функции для ручных операций с буфером обмена
        def copy_text(event=None):
            try:
                # Получение выделенного текста
                if isinstance(widget, ctk.CTkEntry):
                    text = widget._entry.selection_get()
                else:
                    text = widget._textbox.selection_get()
                
                widget.clipboard_clear()
                widget.clipboard_append(text)
                widget.update() # Требуется для завершения обновления буфера обмена
            except:
                pass
            return "break"

        def paste_text(event=None):
            try:
                text = widget.clipboard_get()
                if isinstance(widget, ctk.CTkEntry):
                    widget._entry.insert(tk.INSERT, text)
                else:
                    widget._textbox.insert(tk.INSERT, text)
            except:
                pass
            return "break"

        def cut_text(event=None):
            try:
                copy_text()
                if isinstance(widget, ctk.CTkEntry):
                    widget._entry.delete("sel.first", "sel.last")
                else:
                    widget._textbox.delete("sel.first", "sel.last")
            except:
                pass
            return "break"

        def select_all(event=None):
            if isinstance(widget, ctk.CTkEntry):
                widget._entry.select_range(0, tk.END)
                widget._entry.icursor(tk.END)
            else:
                widget._textbox.tag_add("sel", "1.0", "end")
            return "break"

        menu.add_command(label="Копировать", command=copy_text)
        menu.add_command(label="Вставить", command=paste_text)
        menu.add_command(label="Вырезать", command=cut_text)
        menu.add_separator()
        menu.add_command(label="Выделить всё", command=select_all)

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        # Определение целевого внутреннего виджета
        if isinstance(widget, ctk.CTkEntry):
            target = widget._entry
        elif isinstance(widget, ctk.CTkTextbox):
            target = widget._textbox
        else:
            return

        target.bind("<Button-3>", show_menu)
        
        # Привязка клавиш напрямую к этим функциям
        # Стандартные
        target.bind("<Control-c>", copy_text)
        target.bind("<Control-v>", paste_text)
        target.bind("<Control-x>", cut_text)
        target.bind("<Control-a>", select_all)
        
        # Кириллица
        target.bind("<Control-Cyrillic_es>", copy_text)
        target.bind("<Control-Cyrillic_em>", paste_text)
        target.bind("<Control-Cyrillic_che>", cut_text)
        target.bind("<Control-Cyrillic_ef>", select_all)
        
    def load_initial_data(self):
        # Установка параметров проекции по умолчанию
        self.entry_cm.insert(0, "29 59 59,91779")
        self.entry_fe.insert(0, "67119.6943")
        self.entry_fn.insert(0, "-6191992.4462")
        self.entry_scale.insert(0, "1.0")
        self.entry_lat0.insert(0, "0")
        
        # Установка данных WGS84 по умолчанию
        wgs_data = """1,55.9132151,28.7827337,148.13
2,55.9177362,28.8195407,153.07
3,55.8997317,28.8448859,150.32
4,55.8879009,28.8148194,144.81
5,55.8993879,28.7702963,140.8"""
        self.text_wgs.insert("0.0", wgs_data)
        
        # Установка данных МСК по умолчанию
        msk_data = """1,7686.0995773235,-8996.72764806,128.313878864
2,8149.5516395103,-6686.6830560778,133.2730658024
3,6118.3181298608,-5135.559022994,130.5397422902
4,4832.9892219482,-7038.7691853523,125.0153974839
5,6160.4605288561,-9801.7721945621,120.9794011708"""
        self.text_msk.insert("0.0", msk_data)

    def load_file(self, text_widget):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_widget.delete("0.0", "end")
                    text_widget.insert("0.0", content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")

    def parse_text_data(self, text):
        data = []
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            # Разделение по запятой или табуляции
            parts = re.split(r'[,\t]', line)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 4:
                data.append(parts[:4])
        return data

    def calculate_control(self):
        if not self.calculated_params:
            messagebox.showwarning("Внимание", "Сначала рассчитайте параметры!")
            return
            
        try:
            lat = float(self.entry_ctrl_lat.get().replace(',', '.'))
            lon = float(self.entry_ctrl_lon.get().replace(',', '.'))
            h = float(self.entry_ctrl_h.get().replace(',', '.'))
            
            # 1. WGS -> Декартовы
            wx, wy, wz = self.converter.wgs84_to_cartesian(lat, lon, h)
            
            # 2. Применение Хельмерта (WGS Cart -> MSK Cart)
            # Создание массива одной точки
            src = np.array([[wx, wy, wz]])
            transformed = self.estimator.apply_helmert(src, self.calculated_params)
            mx_cart, my_cart, mz_cart = transformed[0]
            
            # 3. MSK Cart -> MSK Projected
            # Получение параметров проекции снова (или их сохранение)
            cm_str = self.entry_cm.get().strip()
            fe = float(self.entry_fe.get().replace(',', '.'))
            fn = float(self.entry_fn.get().replace(',', '.'))
            scale = float(self.entry_scale.get().replace(',', '.'))
            lat0 = float(self.entry_lat0.get().replace(',', '.'))
            cm_deg = self.converter.parse_dms(cm_str)
            
            northing, easting, h_msk = self.converter.cartesian_to_msk(mx_cart, my_cart, mz_cart, cm_deg, fe, fn, scale, lat0)
            
            self.lbl_ctrl_res.configure(text=f"x: {northing:.4f}, y: {easting:.4f}, h: {h_msk:.4f}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {e}")

    def calculate(self):
        try:
            # 1. Парсинг параметров проекции
            cm_str = self.entry_cm.get().strip()
            fe = float(self.entry_fe.get().replace(',', '.'))
            fn = float(self.entry_fn.get().replace(',', '.'))
            scale = float(self.entry_scale.get().replace(',', '.'))
            lat0 = float(self.entry_lat0.get().replace(',', '.'))
            
            cm_deg = self.converter.parse_dms(cm_str)
            
            # 2. Парсинг координат
            wgs_raw = self.parse_text_data(self.text_wgs.get("0.0", "end"))
            msk_raw = self.parse_text_data(self.text_msk.get("0.0", "end"))
            
            if len(wgs_raw) != len(msk_raw):
                self.text_results.delete("0.0", "end")
                self.text_results.insert("0.0", "Ошибка: Количество точек не совпадает.")
                return
            
            if len(wgs_raw) < 3:
                self.text_results.delete("0.0", "end")
                self.text_results.insert("0.0", "Ошибка: Нужно минимум 3 точки.")
                return
                
            # 3. Конвертация и Оценка
            wgs_coords = []
            msk_coords = []
            ids = []
            
            # Сохранение оригинальных МСК для сравнения
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
                
                # MSK -> Декартовы (используя CRS, определенную в pyproj)
                mx, my, mz = self.converter.msk_to_cartesian(northing=m_x, easting=m_y, h=m_h, central_meridian_deg=cm_deg, false_easting=fe, false_northing=fn, scale_factor=scale, lat_origin=lat0)
                msk_coords.append([mx, my, mz])
                
            wgs_coords = np.array(wgs_coords)
            msk_coords = np.array(msk_coords)
            
            # Оценка
            params = self.estimator.calculate_helmert(wgs_coords, msk_coords)
            self.calculated_params = params
            
            # Проверка (Декартовы)
            transformed_cart = self.estimator.apply_helmert(wgs_coords, params)
            
            # Преобразование Трансформированных Декартовых обратно в МСК Проекцию для сравнения
            msk_calculated = []
            for i in range(len(transformed_cart)):
                tx, ty, tz = transformed_cart[i]
                n, e, h = self.converter.cartesian_to_msk(tx, ty, tz, cm_deg, fe, fn, scale, lat0)
                msk_calculated.append([n, e, h])
            
            # Вывод
            res = f"=== Параметры проекции ===\n"
            res += f"CM (deg): {cm_deg:.9f}\n\n"
            
            res += "=== Рассчитанные параметры (WGS84 -> МСК) ===\n"
            res += f"Tx: {params['Tx']:.4f} м\n"
            res += f"Ty: {params['Ty']:.4f} м\n"
            res += f"Tz: {params['Tz']:.4f} м\n"
            res += f"Rx: {params['Rx']:.5f} сек\n"
            res += f"Ry: {params['Ry']:.5f} сек\n"
            res += f"Rz: {params['Rz']:.5f} сек\n"
            res += f"Scale: {params['Scale_ppm']:.5f} ppm\n\n"
            
            res += "=== WKT (для GIS) ===\n"
            wkt = self.estimator.generate_wkt(params, cm_deg, fe, fn, scale, lat0)
            res += wkt + "\n\n"
            
            res += "=== Сравнение координат (МСК Исходные vs МСК Рассчитанные) ===\n"
            res += f"{'ID':<5} | {'X исх':<12} | {'Y исх':<12} | {'X расч':<12} | {'Y расч':<12} | {'dX':<8} | {'dY':<8} | {'dH':<8}\n"
            res += "-"*100 + "\n"
            
            for i in range(len(ids)):
                orig = msk_original[i]
                calc = msk_calculated[i]
                
                dx = orig[0] - calc[0]
                dy = orig[1] - calc[1]
                dh = orig[2] - calc[2]
                
                res += f"{ids[i]:<5} | {orig[0]:<12.4f} | {orig[1]:<12.4f} | {calc[0]:<12.4f} | {calc[1]:<12.4f} | {dx:<8.4f} | {dy:<8.4f} | {dh:<8.4f}\n"
                
            self.text_results.delete("0.0", "end")
            self.text_results.insert("0.0", res)
            
        except Exception as e:
            self.text_results.delete("0.0", "end")
            self.text_results.insert("0.0", f"Ошибка: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = App()
    app.mainloop()
