
from pyproj import Transformer, datadir
from pathlib import Path
import os

# Setup path
current_dir = Path(__file__).parent
project_root = current_dir.parent
assets_dir = project_root / "assets"

if assets_dir.exists():
    datadir.append_data_dir(str(assets_dir))

# Construct a pipeline string that explicitly uses the grid
# WGS84 (4979) -> EGM2008 height
# step 1: vgridshift with the file

pipeline_str = (
    "+proj=pipeline "
    "+step +proj=vgridshift +grids=us_nga_egm2008_1.tif +multiplier=1 "
    "+step +proj=cart +ellps=WGS84"  # Just to check if pipeline works, but actually we want height change
)

# Simpler pipeline: just vgridshift
# Input: Lon, Lat, H_ellips
# Output: Lon, Lat, H_ortho = H_ellips - N
# vgridshift applies the grid value. 
# Usually +inv is needed to go from Ellipsoid to Orthometric? Or vice versa?
# "The grid shift is applied to the vertical component."
# Let's try both directions.

pipeline_simple = "+proj=vgridshift +grids=us_nga_egm2008_1.tif +multiplier=1"

try:
    transformer = Transformer.from_pipeline(pipeline_simple)
    
    lat, lon, h = 55.7558, 37.6173, 200.0
    
    # Note: vgridshift expects (lon, lat, z)
    res = transformer.transform(lon, lat, h)
    print(f"Pipeline Result: {res}")
    print(f"Diff H: {h - res[2]}")
    
except Exception as e:
    print(f"Pipeline Error: {e}")
