import numpy as np
from src.core.logger import logger

class ParameterEstimator:
    def calculate_helmert(self, source_coords, target_coords):
        """
        Расчет 7 параметров (Tx, Ty, Tz, Rx, Ry, Rz, m) для преобразования источника в цель.
        """
        try:
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
            
            result = {
                "Tx": Tx, "Ty": Ty, "Tz": Tz,
                "Rx": Rx_sec, "Ry": Ry_sec, "Rz": Rz_sec,
                "Scale_ppm": Scale_ppm
            }
            logger.info(f"Рассчитаны параметры Хельмерта: {result}")
            return result
        except Exception as e:
            logger.exception("Ошибка в calculate_helmert")
            raise

    def apply_helmert(self, source_coords, params):
        """
        Применение рассчитанных параметров к исходным координатам для проверки.
        """
        try:
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
            
            logger.debug(f"Применена трансформация Хельмерта к {len(source_coords)} точкам")
            return np.array(transformed)
        except Exception as e:
            logger.exception("Ошибка в apply_helmert")
            raise

    def generate_wkt(self, params, cm_deg, fe, fn, scale, lat0, use_geoid=False):
        """
        Генерация строки WKT для рассчитанных параметров.
        """
        try:
            # Инвертирование Переноса и Масштаба
            tx = -params['Tx']
            ty = -params['Ty']
            tz = -params['Tz']
            s = -params['Scale_ppm']
            
            # Вращения остаются как есть (предполагая конвенцию PV для WKT)
            rx = params['Rx']
            ry = params['Ry']
            rz = params['Rz']
            
            # Базовая строка PROJCS
            projcs = f'''PROJCS["unknown",
    GEOGCS["unknown",
        DATUM["Krassovsky, 1942",
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

            if use_geoid:
                wkt = f'''COMPD_CS["unknown + EGM2008 geoid height",
\t{projcs},
\tVERT_CS["EGM2008 geoid height",
\t\tVERT_DATUM["EGM2008  geoid",2005,AUTHORITY["EPSG","1027"]],
\t\tUNIT["metre",1,AUTHORITY["EPSG","9001"]],
\tAUTHORITY["EPSG","3855"]]]'''
            else:
                wkt = projcs

            logger.debug(f"Сгенерирована строка WKT (geoid={use_geoid})")
            return wkt
            logger.debug("Сгенерирована строка WKT")
            return wkt
        except Exception as e:
            logger.exception("Ошибка генерации WKT")
            raise
