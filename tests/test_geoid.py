
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator

@pytest.fixture
def converter():
    return CoordinateConverter()

@pytest.fixture
def estimator():
    return ParameterEstimator()

def test_geoid_transformation(converter, estimator):
    """
    Проверка того, что при наличии геоида в WKT происходит трансформация высоты.
    """
    # 1. Генерация WKT с геоидом
    params = {
        "Tx": 0, "Ty": 0, "Tz": 0,
        "Rx": 0, "Ry": 0, "Rz": 0,
        "Scale_ppm": 0
    }
    
    # Используем параметры, близкие к реальности, или просто нули, так как нас интересует вертикальный сдвиг
    wkt_with_geoid = estimator.generate_wkt(params, cm_deg=30, fe=500000, fn=0, scale=1, lat0=0, use_geoid=True)
    
    # 2. Тестовая точка (Москва)
    lat, lon, h_ellips = 55.7558, 37.6173, 200.0
    
    # 3. Трансформация
    try:
        n, e, h_ortho = converter.wkt_to_msk(wkt_with_geoid, lat, lon, h_ellips)
        
        print(f"Input H (Ellipsoid): {h_ellips}")
        print(f"Output H (Orthometric): {h_ortho}")
        
        # Разница должна быть не нулевой, если геоид применился
        # В Москве волна геоида EGM2008 около 10-15 метров
        diff = h_ellips - h_ortho
        print(f"Geoid Undulation (approx): {diff}")
        
        assert abs(diff) > 1.0, "Высота не изменилась, возможно геоид не применился"
        
    except Exception as e:
        pytest.fail(f"Ошибка трансформации: {e}")

def test_no_geoid_transformation(converter, estimator):
    """
    Проверка того, что без геоида высота не меняется (или меняется минимально из-за проекции, если бы она была геоцентрической, но тут МСК 2D+H).
    """
    params = {
        "Tx": 0, "Ty": 0, "Tz": 0,
        "Rx": 0, "Ry": 0, "Rz": 0,
        "Scale_ppm": 0
    }
    
    wkt_no_geoid = estimator.generate_wkt(params, cm_deg=30, fe=500000, fn=0, scale=1, lat0=0, use_geoid=False)
    
    lat, lon, h_ellips = 55.7558, 37.6173, 200.0
    
    n, e, h_res = converter.wkt_to_msk(wkt_no_geoid, lat, lon, h_ellips)
    
    # Без геоида высота должна остаться эллипсоидальной (или близкой к ней, если нет 7 параметров)
    # В нашей реализации если нет геоида, используется EPSG:4326 -> 2D MSK. 
    # Но метод wkt_to_msk возвращает h_msk. 
    # Если исходная 4326 (2D), то transform(lon, lat, h) вернет 2 значения или 3?
    # Transformer(4326, MSK_2D) -> transform(x,y,z) -> (x', y', z) обычно z пробрасывается.
    
    print(f"Input H: {h_ellips}")
    print(f"Output H: {h_res}")
    
    assert h_res == pytest.approx(h_ellips, abs=1e-3)
