
from pyproj import Transformer, datadir
from pathlib import Path
import os

# Setup path
current_dir = Path(__file__).parent
project_root = current_dir.parent
assets_dir = project_root / "assets"

if assets_dir.exists():
    datadir.append_data_dir(str(assets_dir))

# Try with +inv
# We want H_ortho = H_ellips - N
# If N is positive (Moscow ~14.5m), H_ortho should be < H_ellips.

pipeline_inv = "+proj=vgridshift +grids=us_nga_egm2008_1.tif +multiplier=1 +inv"

try:
    transformer = Transformer.from_pipeline(pipeline_inv)
    
    lat, lon, h = 55.7558, 37.6173, 200.0
    
    res = transformer.transform(lon, lat, h)
    print(f"Pipeline (+inv) Result: {res}")
    print(f"Diff H: {h - res[2]}")
    
except Exception as e:
    print(f"Pipeline Error: {e}")
