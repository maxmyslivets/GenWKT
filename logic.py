import numpy as np
from pyproj import CRS, Transformer
import re

class CoordinateConverter:
    def __init__(self):
        pass

    def parse_dms(self, dms_str):
        """
        Парсинг строки DMS вида "29 59 59,91779" или "29 59 59.91779" в десятичные градусы.
        Ожидаемый формат: Градусы Минуты Секунды.
        """
        try:
            # Замена запятой на точку
            dms_str = dms_str.replace(',', '.')
            parts = dms_str.split()
            if len(parts) != 3:
                raise ValueError("Неверный формат DMS. Ожидается 'ГГ ММ СС.сссс'")
            
            d = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            
            sign = 1
            if d < 0:
                sign = -1
                d = abs(d)
            
            return sign * (d + m / 60 + s / 3600)
        except Exception as e:
            raise ValueError(f"Ошибка парсинга DMS '{dms_str}': {e}")

    def wgs84_to_cartesian(self, lat, lon, h):
        """
        Преобразование WGS84 (lat, lon, h) в Геоцентрические (X, Y, Z).
        """
        # WGS84 Геодезическая
        crs_geo = CRS.from_epsg(4326) # Lat, Lon
        # WGS84 Геоцентрическая (Декартова)
        crs_cart = CRS.from_epsg(4978) 
        
        transformer = Transformer.from_crs(crs_geo, crs_cart, always_xy=True)
        # pyproj always_xy=True означает порядок (lon, lat) для EPSG:4326 обычно, 
        # но нужно быть осторожным. Определение EPSG:4326 в PROJ - это порядок Lat, Lon.
        # Однако поведение Transformer.from_crs зависит от версии PROJ и входных данных.
        # Безопаснее использовать always_xy=True и передавать (lon, lat).
        
        X, Y, Z = transformer.transform(lon, lat, h)
        return X, Y, Z

    def msk_to_cartesian(self, northing, easting, h, central_meridian_deg, false_easting=500000, false_northing=0, scale_factor=1.0, lat_origin=0):
        """
        Преобразование МСК (Поперечная Меркатора на Красовском) в Геоцентрические (X, Y, Z на Красовском).
        """
        # Определение CRS МСК
        # +proj=tmerc +lat_0=0 +lon_0={cm} +k={scale} +x_0={fe} +y_0={fn} +ellps=krass +units=m +no_defs
        proj_str = (f"+proj=tmerc +lat_0={lat_origin} +lon_0={central_meridian_deg} "
                    f"+k={scale_factor} +x_0={false_easting} +y_0={false_northing} "
                    f"+ellps=krass +units=m +no_defs")
        
        crs_msk = CRS.from_proj4(proj_str)
        
        # Определение Геоцентрической CRS Красовского
        # +proj=geocent +ellps=krass +units=m +no_defs
        crs_cart = CRS.from_proj4("+proj=geocent +ellps=krass +units=m +no_defs")
        
        transformer = Transformer.from_crs(crs_msk, crs_cart, always_xy=True)
        
        # Входные данные: Easting (x), Northing (y) для always_xy=True
        X, Y, Z = transformer.transform(easting, northing, h)
        return X, Y, Z

    def cartesian_to_msk(self, X, Y, Z, central_meridian_deg, false_easting=500000, false_northing=0, scale_factor=1.0, lat_origin=0):
        """
        Преобразование Геоцентрических (X, Y, Z на Красовском) в МСК (Поперечная Меркатора на Красовском).
        """
        proj_str = (f"+proj=tmerc +lat_0={lat_origin} +lon_0={central_meridian_deg} "
                    f"+k={scale_factor} +x_0={false_easting} +y_0={false_northing} "
                    f"+ellps=krass +units=m +no_defs")
        
        crs_msk = CRS.from_proj4(proj_str)
        crs_cart = CRS.from_proj4("+proj=geocent +ellps=krass +units=m +no_defs")
        
        # Обратный трансформер: Cart -> MSK
        transformer = Transformer.from_crs(crs_cart, crs_msk, always_xy=True)
        
        # Выходные данные: Easting (x), Northing (y)
        easting, northing, h = transformer.transform(X, Y, Z)
        return northing, easting, h

    def wkt_to_msk(self, wkt_str, lat, lon, h):
        """
        Преобразование WGS84 (Lat, Lon, H) в МСК с использованием строки WKT.
        """
        try:
            crs_msk = CRS.from_wkt(wkt_str)
            crs_wgs = CRS.from_epsg(4326) # Lat, Lon
            
            # Проверка порядка осей WKT CRS
            # pyproj/PROJ чувствителен к порядку осей. 
            # Мы используем always_xy=True, чтобы принудительно использовать конвенцию (Lon, Lat) -> (Easting, Northing), если это возможно,
            # но для WKT это зависит от определения AXIS в строке.
            
            transformer = Transformer.from_crs(crs_wgs, crs_msk, always_xy=True)
            
            # Трансформация (Lon, Lat, H) -> (Easting, Northing, H)
            easting, northing, h_msk = transformer.transform(lon, lat, h)
            
            # Возврат Northing (x), Easting (y), H
            return northing, easting, h_msk
        except Exception as e:
            raise ValueError(f"Ошибка в преобразовании WKT: {e}")

class ParameterEstimator:
    def calculate_helmert(self, source_coords, target_coords):
        """
        Расчет 7 параметров (Tx, Ty, Tz, Rx, Ry, Rz, m) для преобразования источника в цель.
        Основано на формулах из 13.mhtml (Серапинас).
        
        Уравнения:
        vX = Tx + m*X + wz*Y - wy*Z - (Xt - Xs)
        vY = Ty - wz*X + m*Y + wx*Z - (Yt - Ys)
        vZ = Tz + wy*X - wx*Y + m*Z - (Zt - Zs)
        
        Неизвестные: [Tx, Ty, Tz, wx, wy, wz, m]
        """
        n = len(source_coords)
        if n < 3:
            raise ValueError("Нужно минимум 3 точки для оценки 7 параметров")
            
        A = np.zeros((3 * n, 7))
        L = np.zeros((3 * n))
        
        for i in range(n):
            src = source_coords[i] # Xs, Ys, Zs
            tgt = target_coords[i] # Xt, Yt, Zt
            
            X, Y, Z = src
            
            # L = Цель - Источник
            L[3*i]     = tgt[0] - src[0]
            L[3*i + 1] = tgt[1] - src[1]
            L[3*i + 2] = tgt[2] - src[2]
            
            # Коэффициенты для Tx, Ty, Tz
            A[3*i, 0] = 1
            A[3*i + 1, 1] = 1
            A[3*i + 2, 2] = 1
            
            # Коэффициенты для wx (Rx)
            A[3*i, 3] = 0
            A[3*i + 1, 3] = Z
            A[3*i + 2, 3] = -Y
            
            # Коэффициенты для wy (Ry)
            A[3*i, 4] = -Z
            A[3*i + 1, 4] = 0
            A[3*i + 2, 4] = X
            
            # Коэффициенты для wz (Rz)
            A[3*i, 5] = Y
            A[3*i + 1, 5] = -X
            A[3*i + 2, 5] = 0
            
            # Коэффициенты для m (Масштаб)
            A[3*i, 6] = X
            A[3*i + 1, 6] = Y
            A[3*i + 2, 6] = Z
            
        # Решение нормальных уравнений
        x, residuals, rank, s = np.linalg.lstsq(A, L, rcond=None)
        
        # Извлечение параметров
        Tx, Ty, Tz = x[0], x[1], x[2]
        Rx_rad, Ry_rad, Rz_rad = x[3], x[4], x[5]
        m = x[6]
        
        # Преобразование вращений в угловые секунды
        Rx_sec = np.degrees(Rx_rad) * 3600
        Ry_sec = np.degrees(Ry_rad) * 3600
        Rz_sec = np.degrees(Rz_rad) * 3600
        
        Scale_ppm = m * 1e6
        
        return {
            "Tx": Tx, "Ty": Ty, "Tz": Tz,
            "Rx": Rx_sec, "Ry": Ry_sec, "Rz": Rz_sec,
            "Scale_ppm": Scale_ppm
        }

    def apply_helmert(self, source_coords, params):
        """
        Применение рассчитанных параметров к исходным координатам для проверки.
        Используется та же структура формул, что и при оценке.
        """
        Tx, Ty, Tz = params["Tx"], params["Ty"], params["Tz"]
        m = params["Scale_ppm"] * 1e-6
        wx = np.radians(params["Rx"] / 3600)
        wy = np.radians(params["Ry"] / 3600)
        wz = np.radians(params["Rz"] / 3600)
        
        transformed = []
        for src in source_coords:
            X, Y, Z = src
            
            # X_new = X + Tx + m*X + wz*Y - wy*Z
            X_t = X + Tx + m*X + wz*Y - wy*Z
            
            # Y_new = Y + Ty - wz*X + m*Y + wx*Z
            Y_t = Y + Ty - wz*X + m*Y + wx*Z
            
            # Z_new = Z + Tz + wy*X - wx*Y + m*Z
            Z_t = Z + Tz + wy*X - wx*Y + m*Z
            
            transformed.append([X_t, Y_t, Z_t])
            
        return np.array(transformed)

    def generate_wkt(self, params, cm_deg, fe, fn, scale, lat0):
        """
        Генерация строки WKT для рассчитанных параметров.
        Примечание: Параметры TOWGS84 определяют преобразование ОТ локального датума К WGS84.
        Наши рассчитанные параметры - ОТ WGS84 К Локальному.
        Поэтому мы должны инвертировать Перенос и Масштаб.
        
        Для Вращений:
        - Мы рассчитали Вращение Координатной Рамки (CFR) от WGS84 к Локальному.
        - TOWGS84 обычно ожидает Вектор Позиции (PV) от Локального к WGS84.
        - PV(Локальный->WGS84) численно равен CFR(WGS84->Локальный).
        - Поэтому мы оставляем Вращения КАК ЕСТЬ.
        """
        # Инвертирование Переноса и Масштаба
        tx = -params['Tx']
        ty = -params['Ty']
        tz = -params['Tz']
        s = -params['Scale_ppm']
        
        # Вращения остаются как есть (предполагая конвенцию PV для WKT)
        rx = params['Rx']
        ry = params['Ry']
        rz = params['Rz']
        
        wkt = f'''PROJCS["unknown",
    GEOGCS["unknown",
        DATUM["Unknown based on Krassovsky, 1942 ellipsoid",
            SPHEROID["Krassovsky, 1942",6378245,298.3],
            TOWGS84[{tx:.9f},{ty:.9f},{tz:.9f},{rx:.9f},{ry:.9f},{rz:.9f},{s:.9f}]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",{lat0}],
    PARAMETER["central_meridian",{cm_deg}],
    PARAMETER["scale_factor",{scale}],
    PARAMETER["false_easting",{fe}],
    PARAMETER["false_northing",{fn}],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]]'''
        return wkt
