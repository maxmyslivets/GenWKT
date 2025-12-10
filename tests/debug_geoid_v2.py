
import sys
import os
from pyproj import CRS, Transformer

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.estimator import ParameterEstimator

def test_geoid_transform_3d():
    estimator = ParameterEstimator()

    # 1. Generate WKT with Geoid
    params = {
        "Tx": 0, "Ty": 0, "Tz": 0,
        "Rx": 0, "Ry": 0, "Rz": 0,
        "Scale_ppm": 0
    }
    
    wkt_with_geoid = estimator.generate_wkt(params, cm_deg=30, fe=500000, fn=0, scale=1, lat0=0, use_geoid=True)
    wkt_no_geoid = estimator.generate_wkt(params, cm_deg=30, fe=500000, fn=0, scale=1, lat0=0, use_geoid=False)

    lat, lon, h_ellips = 55.0, 37.0, 200.0

    print("--- Test 1: Source 4979 (3D) -> Target Compound (Geoid) ---")
    try:
        crs_src = CRS.from_epsg(4979)
        crs_tgt = CRS.from_wkt(wkt_with_geoid)
        transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
        res = transformer.transform(lon, lat, h_ellips)
        print(f"Result: {res}")
        if len(res) == 3:
             print(f"Diff H: {h_ellips - res[2]}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test 2: Source 4979 (3D) -> Target 2D (No Geoid) ---")
    try:
        crs_src = CRS.from_epsg(4979)
        crs_tgt = CRS.from_wkt(wkt_no_geoid)
        transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
        res = transformer.transform(lon, lat, h_ellips)
        print(f"Result: {res}")
        # If target is 2D, does it return 2 or 3 values?
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test 3: Source 4326 (2D) -> Target Compound (Geoid) ---")
    try:
        crs_src = CRS.from_epsg(4326)
        crs_tgt = CRS.from_wkt(wkt_with_geoid)
        transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
        res = transformer.transform(lon, lat, h_ellips)
        print(f"Result: {res}")
        if len(res) == 3:
             print(f"Diff H: {h_ellips - res[2]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_geoid_transform_3d()
