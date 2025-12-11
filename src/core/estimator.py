import numpy as np
from src.core.logger import logger
from scipy.optimize import minimize
from pyproj import CRS, Transformer

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
        except Exception as e:
            logger.exception("Ошибка генерации WKT")
            raise

    def estimate_projection_parameters(self, wgs_points, msk_points, fixed_scale=True):
        """
        Оценка параметров проекции (CM, Scale, FE, FN) по набору точек.
        wgs_points: список [lat, lon, h]
        msk_points: список [x, y, h]
        fixed_scale: если True, масштаб фиксируется равным 1.0 (для ГК/МСК).
        """
        try:
            wgs_points = np.array(wgs_points)
            msk_points = np.array(msk_points)
            
            # Начальные приближения
            avg_lon = np.mean(wgs_points[:, 1])
            
            # Предварительная оценка FE/FN
            # Проецируем с FE=0, FN=0, Scale=1
            proj_str_init = (f"+proj=tmerc +lat_0=0 +lon_0={avg_lon} "
                             f"+k=1.0 +x_0=0 +y_0=0 "
                             f"+ellps=krass +units=m +no_defs")
            crs_msk_init = CRS.from_proj4(proj_str_init)
            crs_wgs = CRS.from_epsg(4326)
            transformer_init = Transformer.from_crs(crs_wgs, crs_msk_init, always_xy=True)
            
            xs_init, ys_init = transformer_init.transform(wgs_points[:, 1], wgs_points[:, 0])
            
            # FE = Mean(MSK_Easting - Proj_Easting)
            fe_guess = np.mean(msk_points[:, 1] - xs_init)
            # FN = Mean(MSK_Northing - Proj_Northing)
            fn_guess = np.mean(msk_points[:, 0] - ys_init)
            
            initial_guess = [avg_lon, fe_guess, fn_guess] # CM, FE, FN
            
            logger.debug(f"Начальные приближения: {initial_guess}, Fixed Scale: {fixed_scale}")
            
            # Целевая функция для минимизации (общая)
            def objective(params):
                if len(params) == 3:
                    cm, fe, fn = params
                    scale = 1.0
                else:
                    cm, scale, fe, fn = params
                
                # Ограничение на масштаб
                if scale <= 1e-4:
                    return 1e20
                
                try:
                    # Создаем временную проекцию
                    proj_str = (f"+proj=tmerc +lat_0=0 +lon_0={cm} "
                               f"+k={scale} +x_0={fe} +y_0={fn} "
                               f"+ellps=krass +units=m +no_defs")
                    crs_msk = CRS.from_proj4(proj_str)
                    transformer = Transformer.from_crs(crs_wgs, crs_msk, always_xy=True)
                    
                    # Проецируем все точки
                    lons = wgs_points[:, 1]
                    lats = wgs_points[:, 0]
                    
                    xs, ys = transformer.transform(lons, lats)
                    
                    # Считаем невязки
                    diff_easting = xs - msk_points[:, 1] 
                    diff_northing = ys - msk_points[:, 0]
                    
                    return np.sum(diff_easting**2 + diff_northing**2)
                except Exception:
                    return 1e20

            # Этап 1: Оптимизация CM, FE, FN (Scale=1.0)
            logger.debug("Запуск оптимизации (Scale=1.0)...")
            res1 = minimize(objective, initial_guess, method='Nelder-Mead', options={'maxiter': 1000})
            
            if not res1.success:
                logger.warning(f"Оптимизация (Scale=1.0) не сошлась: {res1.message}")
            
            cm, fe, fn = res1.x
            scale = 1.0
            
            # Этап 2: Если scale не фиксирован, оптимизируем все параметры
            if not fixed_scale:
                initial_guess_2 = [cm, 1.0, fe, fn]
                logger.debug("Запуск 2 этапа оптимизации (все параметры)...")
                res2 = minimize(objective, initial_guess_2, method='Nelder-Mead', options={'maxiter': 1000})
                
                if not res2.success:
                    logger.warning(f"Оптимизация (все параметры) не сошлась: {res2.message}")
                
                cm, scale, fe, fn = res2.x

            logger.info(f"Оцененные параметры проекции: CM={cm}, Scale={scale}, FE={fe}, FN={fn}")
            
            return {
                "central_meridian": cm,
                "scale_factor": scale,
                "false_easting": fe,
                "false_northing": fn
            }
            
        except Exception as e:
            logger.exception("Ошибка при оценке параметров проекции")
            raise

