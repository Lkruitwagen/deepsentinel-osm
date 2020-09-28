
import os, logging, json

from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely import geometry

from osm_server.utils import wgs2web
from osm_server.models import OSMLine, OSMRoads, OSMPolygon, OSMPoint

app = Flask(__name__)
app.logger = logging.getLogger("flask")
app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logging.StreamHandler())

CONTINENTS = ["europe","central-america","antactica","oceania","asia","south-america","north-america","africa"]


if "BASIC_AUTH_USERNAME" in os.environ:
    app.config["BASIC_AUTH_USERNAME"] = os.environ["BASIC_AUTH_USERNAME"]
    app.config["BASIC_AUTH_PASSWORD"] = os.environ["BASIC_AUTH_PASSWORD"]
    app.config["BASIC_AUTH_FORCE"] = True
    basic_auth = BasicAuth(app)


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/query", methods=["POST"])
def api_query():

    if "geom_type" not in request.form.keys():
        return jsonify({'error': '"geom_type" not in request body keys. Got: {}'.format(','.join(request.form.keys()))})

    if request.form.get("geom_type") not in ['points','polygons','lines']:
        return jsonify({'error':'"geom_type" must be one of ["points","polygons","lines"]. got: {}'.format(request.args.get('geom_type'))})
    elif request.form.get("geom_type")=='points':
        OSM_OBJ = OSMPoint
    elif request.form.get("geom_type")=='polygons':
        OSM_OBJ = OSMPolygon
    elif request.form.get("geom_type")=='lines':
        OSM_OBJ = OSMLine

    if 'feature' not in request.form.keys():
        return jsonify({'error': '"feature" not in request body keys. Got: {}'.format(','.join(request.form.keys()))})
    else:
        ft = json.loads(request.form["feature"])

    ## TODO: validate geojson
    print ('ft',ft, ft['properties'].keys(), ft['geometry'].keys())

    if 'continent' not in ft['properties'].keys():
        return jsonify({'error':'"continent" must be specified in feature properties.'})

    continent = ft["properties"]["continent"]

    if continent not in CONTINENTS:
        return jsonify({'error':'"continent" must be one of {}'.format(','.join(CONTINENTS))})

    geom = geometry.shape(ft['geometry'])

    #attr_columns = []
    #for kk,vv in vars(OSM_OBJ).items():
    #    print ('kk',kk)
    #    if not (kk.startswith('_') or kk=='metadata' or kk=='way'):
    #        print ('getting')
    #        attr_columns.append(vv)
    #print ('attr columns',attr_columns)

    attr_columns = [vv for kk,vv in vars(OSM_OBJ).items() if not (kk.startswith('_') or kk=='metadata' or kk=='way')]
    geom_column = OSM_OBJ.way.ST_Intersection(from_shape(wgs2web(geom), srid=3857))
    query_columns = attr_columns+[geom_column]

    print ('query cols', query_columns)

    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    query = session.query(*query_columns).filter(OSM_OBJ.way.ST_Intersects(from_shape(wgs2web(geom), srid=3857)))

    result = query.all()

    results_json = []

    for ii_r, r in enumerate(result):
        print ('r',r)
        print ('dir',dir(r))
        res_dict = {}

        res_dict['properties'] = {kk:r.__getattribute__(kk) for kk in dir(OSM_OBJ) if not (kk.startswith('_') or kk=='metadata' or kk=='way') and r.__getattribute__(kk) is not None}
        res_dict['geometry'] = str(r[-1])#.way)

        results_json.append(res_dict)

    results_json = {'features': results_json}

    print ('results_json',results_json)

    return jsonify(results_json)

if __name__ =="__main__":
    app.run(host="0.0.0.0")
