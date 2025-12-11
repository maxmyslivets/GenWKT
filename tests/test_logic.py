import pytest
import numpy as np
from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator

@pytest.fixture
def converter():
    return CoordinateConverter()

@pytest.fixture
def estimator():
    return ParameterEstimator()

def test_parse_dms(converter):
    assert converter.parse_dms("29 59 59,91779") == pytest.approx(29.99997716, abs=1e-8)
    assert converter.parse_dms("0 0 0") == 0
    with pytest.raises(ValueError):
        converter.parse_dms("invalid")

def test_wgs84_to_cartesian(converter):
    # Тестовая точка
    lat, lon, h = 55.0, 37.0, 100.0
    x, y, z = converter.wgs84_to_cartesian(lat, lon, h)
    assert isinstance(x, float)
    assert isinstance(y, float)
    assert isinstance(z, float)

def test_helmert_calculation(estimator):
    # Создание синтетических данных
    # Тождественное преобразование (без сдвига, без вращения, масштаб 1)
    src = np.array([
        [1000, 2000, 3000],
        [1100, 2100, 3100],
        [1200, 2200, 3200]
    ])
    tgt = src # Те же точки
    
    params = estimator.calculate_helmert(src, tgt)
    
    assert params["Tx"] == pytest.approx(0, abs=1e-9)
    assert params["Rx"] == pytest.approx(0, abs=1e-9)
    assert params["Scale_ppm"] == pytest.approx(0, abs=1e-9)

def test_helmert_shift(estimator):
    src = np.array([
        [1000, 2000, 3000],
        [1100, 2100, 3100],
        [1200, 2200, 3200]
    ])
    # Сдвиг на 10, 20, 30
    tgt = src + np.array([10, 20, 30])
    
    params = estimator.calculate_helmert(src, tgt)
    
    assert params["Tx"] == pytest.approx(10, abs=1e-9)
    assert params["Ty"] == pytest.approx(20, abs=1e-9)
    assert params["Tz"] == pytest.approx(30, abs=1e-9)
