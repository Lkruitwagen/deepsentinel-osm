import pyproj
from functools import partial

PROJ_WGS = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
PROJ_WEB = pyproj.Proj('epsg:3857')

wgs2web = partial(pyproj.transform, PROJ_WGS, PROJ_WEB)
web2wgs = partial(pyproj.transform, PROJ_WEB, PROJ_WGS)

