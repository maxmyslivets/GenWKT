
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator

def test_geoid_transform():
    converter = CoordinateConverter()
    estimator = ParameterEstimator()

    # 1. Generate WKT with Geoid
    # Using dummy parameters for MSK
    params = {
        "Tx": 0, "Ty": 0, "Tz": 0,
        "Rx": 0, "Ry": 0, "Rz": 0,
        "Scale_ppm": 0
    }
    # EGM2008 is usually large, let's see if pyproj handles it or if we need a simpler test case.
    # Or we can just check if the WKT parsing works and if it attempts a vertical transform.
    
    wkt_with_geoid = estimator.generate_wkt(params, cm_deg=30, fe=500000, fn=0, scale=1, lat0=0, use_geoid=True)
    print("WKT with Geoid:")
    print(wkt_with_geoid)

    # 2. Try transform
    # WGS84 point
    lat, lon, h_ellips = 55.0, 37.0, 200.0
    
    try:
        n, e, h_ortho = converter.wkt_to_msk(wkt_with_geoid, lat, lon, h_ellips)
        print(f"Input: Lat={lat}, Lon={lon}, H_ellips={h_ellips}")
        print(f"Output: N={n}, E={e}, H_ortho={h_ortho}")
        
        # If H_ortho is significantly different from H_ellips (approx geoid separation), it works.
        # In Moscow region, geoid undulation is around ~10-15 meters?
        # If H_ortho == H_ellips, then no vertical transform happened.
        
        diff = h_ellips - h_ortho
        print(f"Difference (Undulation?): {diff}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_geoid_transform()
