import numpy as np
import json, geojson, overpy, pyproj, logging
from shapely import geometry
from shapely.ops import transform,linemerge, unary_union, polygonize, cascaded_union
from functools import partial
import matplotlib.pyplot as plt

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class LabelCube:
    ### Get the data
    ### Get the map
    ### Get a google basemap or something

    def __init__(self, json_path, resolution, side_length):
        self.resolution = resolution   #m/pix
        self.side_length = side_length  #m
        self.labels_json = json.load(open(json_path,'r'))
        WGS84 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        self.wgs_proj = pyproj.Proj(WGS84)
        self.api = overpy.Overpass()
        self.json_spec = json.load(open(json_path,'r'))

    def get_utm_zone(self, lat,lon):
        zone_str = str(int((lon + 180)/6) + 1)

        if ((lat>=56.) & (lat<64.) & (lon >=3.) & (lon <12.)):
            zone_str = '32'
        elif ((lat >= 72.) & (lat <84.)):
            if ((lon >=0.) & (lon<9.)):
                zone_str = '31'
            elif ((lon >=9.) & (lon<21.)):
                zone_str = '33'
            elif ((lon >=21.) & (lon<33.)):
                zone_str = '35'
            elif ((lon >=33.) & (lon<42.)):
                zone_str = '37'

        return zone_str

    def _set_utm_proj(self,lat,lon):
        self.utm_zone = self.get_utm_zone(lat,lon)
        self.utm_proj = pyproj.Proj(proj='utm', zone=self.utm_zone, ellps='WGS84')
        self.projection_for = partial(pyproj.transform, self.wgs_proj, self.utm_proj)
        self.projection_rev = partial(pyproj.transform, self.utm_proj, self.wgs_proj)


    def _get_bbox(self,lat,lon):

        pt_utm = transform(self.projection_for,geometry.Point(lat,lon))

        bbox_utm = geometry.box(pt_utm.x-self.side_length/2,
                                pt_utm.y-self.side_length/2,
                                pt_utm.x+self.side_length/2,
                                pt_utm.y+self.side_length/2)

        self.bbox_ll = transform(self.projection_rev, bbox_utm)
        #bb = self.bbox_ll.bounds

        #(bb[1],bb[0],bb[3],bb[2])
        return self.bbox_ll.bounds


    def _parse_osm(self, response):

        def _parse_waygeom(way):
            ls_coords = []
            for node in way.nodes:
                ls_coords.append((node.lon,node.lat))
            return geometry.Polygon(ls_coords)

        def _parse_multiway_geom(wayslike,ob_type):
            lss = []
            for ii_w,item in enumerate(wayslike):
                ls_coords = []
                print('way',ii_w)
                if ob_type=='way':
                    for node in item.nodes:
                        ls_coords.append((node.lon,node.lat))
                elif ob_type=='relation':
                    for geom in item.geometry:
                        ls_coords.append((geom.lon, geom.lat))
                lss.append(geometry.LineString(ls_coords))

            merged = linemerge([*lss])
            borders = unary_union(merged)
            polygons = list(polygonize(borders))
            big_geom = cascaded_union(polygons)

            if big_geom.type=='MultiPolygon':
                return list(big_geom)
            elif big_geom.type=='Polygon':
                return [big_geom]

        def _parse_relation(relation):

            outer_mems = [mem for mem in relation.members if mem.role in ['outer','part']]
            inner_mems = [mem for mem in relation.members if mem.role=='inner']

            outer_geom = _parse_multiway_geom(outer_mems,'relation')
            inner_geom = _parse_multiway_geom(inner_mems,'relation')

            rel_geom = geometry.MultiPolygon(outer_geom).difference(geometry.MultiPolygon(inner_geom))

            return geojson.Feature(geometry=rel_geom, properties=relation.attributes)


        gj_fts = []
        for way in response.ways:
            gj_fts.append(geojson.Feature(geometry=_parse_waygeom(way),
                                            properties=way.attributes))
        for relation in response.relations:
            gj_fts.append(_parse_relation(relation))

    def visualise_results(self):
        fig, ax = plt.subplots(1,1,figsize=(12,12))
        for kk,vv in self.osm_results.items():
            rand_col = list(np.random.choice(range(255), size=3)/255)
            for pp in vv:
                xs, ys = pp.exterior.xy
                ax.plot(xs,ys,c=rand_col)
                for hole in pp.interiors:
                    xs,ys = hole.xy
                    ax.plot(xs,ys,c=rand_col)

        plt.show()




    def gen_cube(self, lat, lon):
        self._set_utm_proj(lat,lon)
        bbox = self._get_bbox(lat,lon)

        self.osm_results = {}

        for kk,vv in self.json_spec.items():
            logging.info(f"class key: {kk}, tags: {vv}")
            self.osm_results[kk] = []
            for item in vv:
                logging.info(f"item: {item}")

                query = """[out:json];
                        (
                        node[{item}]{bbox};
                        way[{item}]{bbox};
                        rel[{item}]{bbox};
                        );
                        out geom;
                        >;
                        out skel qt;
                        """.format(bbox=str(bbox),item=item)

                logging.info(f'query:{query}')

                response = self.api.query(query)
                logging.info(f'n nodes: {len(response.nodes)}, n ways: {len(response.ways)}, n relations: {len(response.relations)}')
                logging.info(f'parse osm: {self._parse_osm(response)}')


if __name__ == "__main__":
    labelcube = LabelCube('json_zoo/demo.json',10,350)
    labelcube.gen_cube(51.750084, -1.244094)
    labelcube.visualise_results()



