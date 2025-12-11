import pytest
from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator

def test_parse_dms_decimal():
    converter = CoordinateConverter()
    # Тест десятичных градусов
    assert converter.parse_dms("30.0002885") == 30.0002885
    assert converter.parse_dms("30,0002885") == 30.0002885
    
    # Тест DMS
    # 29 + 59/60 + 59.91779/3600
    expected = 29 + 59/60 + 59.91779/3600
    assert abs(converter.parse_dms("29 59 59,91779") - expected) < 1e-9
    assert abs(converter.parse_dms("29 59 59.91779") - expected) < 1e-9

def test_generate_wkt_geoid():
    estimator = ParameterEstimator()
    params = {
        "Tx": 100, "Ty": 200, "Tz": 300,
        "Rx": 1, "Ry": 2, "Rz": 3,
        "Scale_ppm": 5
    }
    
    # Без геоида
    wkt_simple = estimator.generate_wkt(params, 30.0, 500000, 0, 1.0, 0.0, use_geoid=False)
    assert "PROJCS" in wkt_simple
    assert "COMPD_CS" not in wkt_simple
    
    # С геоидом
    wkt_geoid = estimator.generate_wkt(params, 30.0, 500000, 0, 1.0, 0.0, use_geoid=True)
    assert "COMPD_CS" in wkt_geoid
    assert "EGM2008 geoid height" in wkt_geoid
    assert wkt_simple in wkt_geoid # Проверка вложенности
