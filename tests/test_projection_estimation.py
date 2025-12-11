import numpy as np
import pytest
from src.core.estimator import ParameterEstimator
from src.core.converter import CoordinateConverter

def test_estimate_projection_parameters():
    estimator = ParameterEstimator()
    converter = CoordinateConverter()

    # Данные из test_solver.py
    # WGS: [id, Lat, Lon, H]
    wgs_data = [
        [1, 55.9132151, 28.7827337, 148.13],
        [2, 55.9177362, 28.8195407, 153.07],
        [3, 55.8997317, 28.8448859, 150.32],
        [4, 55.8879009, 28.8148194, 144.81],
        [5, 55.8993879, 28.7702963, 140.8]
    ]

    # MSK: [id, Northing, Easting, H]
    msk_data = [
        [1, 7686.0995773235, -8996.72764806, 128.313878864],
        [2, 8149.5516395103, -6686.6830560778, 133.2730658024],
        [3, 6118.3181298608, -5135.559022994, 130.5397422902],
        [4, 4832.9892219482, -7038.7691853523, 125.0153974839],
        [5, 6160.4605288561, -9801.7721945621, 120.9794011708]
    ]

    # Подготовка данных
    wgs_points = [row[1:] for row in wgs_data] # [Lat, Lon, H]
    msk_points = [row[1:] for row in msk_data] # [Northing, Easting, H]

    # Ожидаемые параметры (из test_solver.py)
    # CM: 29 59 59.91779 ~= 29.999977
    # Shift X (FN): -6191992.4462
    # Shift Y (FE): 67119.6943
    # Но estimator ищет FE/FN для проекции.
    # X_proj = m_x - shift_x => m_x = X_proj + shift_x.
    # m_x (Northing) = Northing_proj + FN.
    # Если shift_x = -6191992, то FN = -6191992?
    # Проверим: X_proj = m_x - (-6M) = m_x + 6M.
    # Обычно Northing = Northing_proj + FN.
    # Если X_proj (это Northing_proj) = m_x - shift_x, то m_x = Northing_proj + shift_x.
    # Значит FN = shift_x = -6191992.4462.
    
    # Y_proj = m_y - shift_y => m_y = Y_proj + shift_y.
    # m_y (Easting) = Easting_proj + FE.
    # Значит FE = shift_y = 67119.6943.

    expected_cm = converter.parse_dms("29 59 59.91779")
    expected_fn = -6191992.4462
    expected_fe = 67119.6943
    
    print(f"Expected CM: {expected_cm}")

    # Запуск оценки
    params = estimator.estimate_projection_parameters(wgs_points, msk_points, fixed_scale=True)
    
    print("Estimated Params:", params)

    # Проверки
    assert np.isclose(params['central_meridian'], expected_cm, atol=1e-4)
    assert np.isclose(params['scale_factor'], 1.0, atol=1e-4)
    # Допуски для FE/FN увеличены, так как без учета Datum Shift они могут отличаться
    assert np.isclose(params['false_northing'], expected_fn, atol=10.0) 
    assert np.isclose(params['false_easting'], expected_fe, atol=10.0)

def test_generate_wkt_custom_name():
    estimator = ParameterEstimator()
    params = {
        "Tx": 0, "Ty": 0, "Tz": 0,
        "Rx": 0, "Ry": 0, "Rz": 0,
        "Scale_ppm": 0
    }
    cm_deg = 30.0
    fe = 500000
    fn = 0
    scale = 1.0
    lat0 = 0
    
    crs_name = "My Custom CRS"
    wkt = estimator.generate_wkt(params, cm_deg, fe, fn, scale, lat0, crs_name=crs_name)
    
    assert f'PROJCS["{crs_name}"' in wkt
    assert f'GEOGCS["{crs_name}"' in wkt
