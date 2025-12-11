import numpy as np
from pyproj import CRS, Transformer, datadir
from pathlib import Path
import os
from src.core.logger import logger

import sys

# Настройка пути к данным PROJ (для геоидов)
if getattr(sys, 'frozen', False):
    # Если приложение собрано PyInstaller
    base_path = Path(sys._MEIPASS)
    assets_dir = base_path / "assets"
else:
    # Если запуск из исходников
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    assets_dir = project_root / "assets"

if assets_dir.exists():
    datadir.append_data_dir(str(assets_dir))
    logger.info(f"Добавлен путь к данным PROJ: {assets_dir}")
else:
    logger.warning(f"Папка assets не найдена по пути: {assets_dir}")

class CoordinateConverter:
    def __init__(self):
        pass

    def parse_dms(self, dms_str: str) -> float:
        """
        Парсинг строки с углом. Поддерживает форматы:
        1. Десятичные градусы: "30.0002885"
        2. DMS: "29 59 59,91779" или "29 59 59.91779" (Градусы Минуты Секунды)
        """
        try:
            # Замена запятой на точку
            dms_str = dms_str.replace(',', '.').strip()
            
            # Попытка распарсить как десятичное число
            try:
                val = float(dms_str)
                logger.debug(f"Распарсены десятичные градусы '{dms_str}' в {val}")
                return val
            except ValueError:
                pass # Не число, пробуем как DMS

            parts = dms_str.split()
            if len(parts) != 3:
                raise ValueError("Неверный формат. Ожидается 'ГГ.гггг' или 'ГГ ММ СС.сссс'")
            
            d = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            
            sign = 1
            if d < 0:
                sign = -1
                d = abs(d)
            
            result = sign * (d + m / 60 + s / 3600)
            logger.debug(f"Распарсен DMS '{dms_str}' в {result}")
            return result
        except Exception as e:
            logger.exception(f"Ошибка парсинга угла '{dms_str}'")
            raise ValueError(f"Ошибка парсинга угла '{dms_str}': {e}")

    def format_dms(self, deg: float) -> str:
        """
        Преобразование десятичных градусов в строку DMS 'ГГ ММ СС.ссссс'.
        """
        try:
            sign = 1
            if deg < 0:
                sign = -1
                deg = abs(deg)
            
            d = int(deg)
            m_full = (deg - d) * 60
            m = int(m_full)
            s = (m_full - m) * 60
            
            # Округление секунд до 5 знаков
            s = round(s, 5)
            
            # Обработка переполнения секунд (60.0 -> 00.0, m+1)
            if s >= 60:
                s = 0
                m += 1
            
            if m >= 60:
                m = 0
                d += 1
                
            if sign == -1:
                d = -d
                
            return f"{d} {m:02d} {s:08.5f}"
        except Exception as e:
            logger.exception(f"Ошибка форматирования угла {deg}")
            return str(deg)

    def wgs84_to_cartesian(self, lat: float, lon: float, h: float):
        """
        Преобразование WGS84 (lat, lon, h) в Геоцентрические (X, Y, Z).
        """
        try:
            # WGS84 Геодезическая
            crs_geo = CRS.from_epsg(4326) # Lat, Lon
            # WGS84 Геоцентрическая (Декартова)
            crs_cart = CRS.from_epsg(4978) 
            
            transformer = Transformer.from_crs(crs_geo, crs_cart, always_xy=True)
            
            X, Y, Z = transformer.transform(lon, lat, h)
            logger.debug(f"Конвертировано WGS84 ({lat}, {lon}, {h}) в Декартовы ({X}, {Y}, {Z})")
            return X, Y, Z
        except Exception as e:
            logger.exception("Ошибка в wgs84_to_cartesian")
            raise

    def msk_to_cartesian(self, northing, easting, h, central_meridian_deg, false_easting=500000, false_northing=0, scale_factor=1.0, lat_origin=0):
        """
        Преобразование МСК (Поперечная Меркатора на Красовском) в Геоцентрические (X, Y, Z на Красовском).
        """
        try:
            proj_str = (f"+proj=tmerc +lat_0={lat_origin} +lon_0={central_meridian_deg} "
                        f"+k={scale_factor} +x_0={false_easting} +y_0={false_northing} "
                        f"+ellps=krass +units=m +no_defs")
            
            crs_msk = CRS.from_proj4(proj_str)
            crs_cart = CRS.from_proj4("+proj=geocent +ellps=krass +units=m +no_defs")
            
            transformer = Transformer.from_crs(crs_msk, crs_cart, always_xy=True)
            
            X, Y, Z = transformer.transform(easting, northing, h)
            logger.debug(f"Конвертировано МСК ({northing}, {easting}, {h}) в Декартовы ({X}, {Y}, {Z})")
            return X, Y, Z
        except Exception as e:
            logger.exception("Ошибка в msk_to_cartesian")
            raise

    def cartesian_to_msk(self, X, Y, Z, central_meridian_deg, false_easting=500000, false_northing=0, scale_factor=1.0, lat_origin=0):
        """
        Преобразование Геоцентрических (X, Y, Z на Красовском) в МСК (Поперечная Меркатора на Красовском).
        """
        try:
            proj_str = (f"+proj=tmerc +lat_0={lat_origin} +lon_0={central_meridian_deg} "
                        f"+k={scale_factor} +x_0={false_easting} +y_0={false_northing} "
                        f"+ellps=krass +units=m +no_defs")
            
            crs_msk = CRS.from_proj4(proj_str)
            crs_cart = CRS.from_proj4("+proj=geocent +ellps=krass +units=m +no_defs")
            
            transformer = Transformer.from_crs(crs_cart, crs_msk, always_xy=True)
            
            easting, northing, h = transformer.transform(X, Y, Z)
            logger.debug(f"Конвертировано Декартовы ({X}, {Y}, {Z}) в МСК ({northing}, {easting}, {h})")
            return northing, easting, h
        except Exception as e:
            logger.exception("Ошибка в cartesian_to_msk")
            raise

    def check_vertical_crs(self, wkt_str: str) -> bool:
        """
        Проверяет, содержит ли WKT описание вертикальной системы координат (EGM2008).
        """
        try:
            crs_msk = CRS.from_wkt(wkt_str)
            
            # Проверка на наличие вертикальной системы координат (EGM2008)
            is_compound = crs_msk.is_compound
            has_egm2008 = False
            if is_compound:
                # Проверяем субисточники, обычно второй - вертикальный
                for sub_crs in crs_msk.sub_crs_list:
                    if sub_crs.is_vertical:
                        # Простая проверка по имени, так как EPSG код может быть не доступен напрямую в имени
                        if "EGM2008" in sub_crs.name or "EGM2008" in sub_crs.to_wkt():
                            has_egm2008 = True
                            break
            return has_egm2008
        except Exception:
            return False

    def wkt_to_msk(self, wkt_str, lat, lon, h):
        """
        Преобразование WGS84 (Lat, Lon, H) в МСК с использованием строки WKT.
        Автоматически определяет необходимость 3D трансформации (если есть геоид).
        """
        try:
            crs_msk = CRS.from_wkt(wkt_str)
            has_egm2008 = self.check_vertical_crs(wkt_str)
            
            h_msk = h
            if has_egm2008:
                # Используем явный пайплайн для EGM2008
                # WGS84 (Ellipsoidal) -> EGM2008 (Orthometric) = h - N
                # vgridshift применяет сдвиг. С +inv он вычитает N (если N положительный).
                # Проверено тестами: +inv дает H = h - N.
                
                # Проверяем наличие файла сетки
                grid_name = "us_nga_egm2008_1.tif"
                grid_path = None
                
                # Ищем в добавленных путях
                # datadir.get_data_dir() возвращает список путей (строка с разделителями)
                # Но мы добавили assets_dir в начало или конец.
                # Проще проверить assets_dir, который мы определили выше
                if (assets_dir / grid_name).exists():
                     pipeline_str = f"+proj=pipeline +step +proj=vgridshift +grids={grid_name} +multiplier=1 +inv"
                     try:
                         pipeline_trans = Transformer.from_pipeline(pipeline_str)
                         # vgridshift ожидает (lon, lat, z)
                         _, _, h_ortho = pipeline_trans.transform(lon, lat, h)
                         h_msk = h_ortho
                         logger.debug(f"Применена трансформация высоты EGM2008: {h} -> {h_msk}")
                     except Exception as e:
                         logger.warning(f"Ошибка при трансформации высоты через pipeline: {e}")
                else:
                    logger.warning(f"Файл сетки {grid_name} не найден, трансформация высоты пропущена.")
            
            # Горизонтальная трансформация (используем 2D WGS84 -> 2D MSK)
            # Даже если WKT Compound, from_crs обычно справляется с горизонтальной частью
            crs_wgs = CRS.from_epsg(4326)
            transformer = Transformer.from_crs(crs_wgs, crs_msk, always_xy=True)
            
            # Трансформируем, но высоту берем из h_msk (если она была изменена)
            # Если трансформер вернет 3 значения, игнорируем Z от него, так как он может быть неточным без сеток
            res = transformer.transform(lon, lat, h)
            
            if len(res) == 3:
                easting, northing, _ = res
            else:
                easting, northing = res
            
            logger.debug(f"Конвертировано WKT WGS84 ({lat}, {lon}, {h}) в МСК ({northing}, {easting}, {h_msk})")
            return northing, easting, h_msk
        except Exception as e:
            logger.exception("Ошибка в преобразовании WKT")
            raise ValueError(f"Ошибка в преобразовании WKT: {e}")
