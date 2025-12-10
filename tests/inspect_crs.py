
from pyproj import CRS

crs = CRS.from_epsg(3855)
print(crs.to_wkt(pretty=True))
print(crs.to_proj4())
