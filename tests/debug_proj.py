
import pyproj
from pyproj import CRS, Transformer, datadir
from pathlib import Path
import os

# Setup path as in converter.py
current_dir = Path(__file__).parent
project_root = current_dir.parent
assets_dir = project_root / "assets"

if assets_dir.exists():
    datadir.append_data_dir(str(assets_dir))
    print(f"Added PROJ data dir: {assets_dir}")

print(f"PROJ Data Dirs: {datadir.get_data_dir()}")

# Check if grid file exists
grid_file = assets_dir / "us_nga_egm2008_1.tif"
print(f"Grid file exists: {grid_file.exists()}")

# Try to create a transformer that explicitly uses the grid
# EPSG:3855 is EGM2008 geoid height
# We want to transform from WGS84 (4979) to WGS84 + EGM2008 height
# But usually we transform WGS84 -> EGM96/2008 directly or use a compound CRS.

try:
    # Create a compound CRS: WGS84 2D + EGM2008 height
    # EGM2008 height is EPSG:3855
    # WGS84 2D is EPSG:4326
    
    # Note: EPSG:3855 definition usually requires the grid file.
    # Let's check what pyproj thinks about 3855
    crs_egm2008 = CRS.from_epsg(3855)
    print("EPSG:3855 Name:", crs_egm2008.name)
    
    # Try a simple vertical transform
    # From Ellipsoidal height (EPSG:4979) to Orthometric height (Compound 4326+3855)
    
    crs_src = CRS.from_epsg(4979)
    crs_tgt = CRS.from_string("EPSG:4326+3855")
    
    transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
    
    lat, lon, h = 55.7558, 37.6173, 200.0
    res = transformer.transform(lon, lat, h)
    print(f"Transform Result: {res}")
    print(f"Diff H: {h - res[2]}")

except Exception as e:
    print(f"Error: {e}")
