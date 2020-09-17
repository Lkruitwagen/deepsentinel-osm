import pyproj
from functools import partial
from shapely import ops

PROJ_WGS = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
PROJ_WEB = pyproj.Proj('epsg:3857')

partial_wgs2web = partial(pyproj.transform, PROJ_WGS, PROJ_WEB)
partial_web2wgs = partial(pyproj.transform, PROJ_WEB, PROJ_WGS)

def wgs2web(geom):
    return ops.transform(partial_wgs2web, geom)

def web2wgs(geom):
    return ops.transform(partial_web2wgs, geom)



