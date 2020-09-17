
import os, logging, json

from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely import geometry, ops

from osm_server.utils import wgs2web
from osm_server.models import OSMLine, OSMRoads, OSMPolygon, OSMPoint

app = Flask(__name__)
app.logger = logging.getLogger("flask")
app.logger.setLevel(logging.ERROR)
app.logger.addHandler(logging.StreamHandler())

if "BASIC_AUTH_USERNAME" in os.environ:
    app.config["BASIC_AUTH_USERNAME"] = os.environ["BASIC_AUTH_USERNAME"]
    app.config["BASIC_AUTH_PASSWORD"] = os.environ["BASIC_AUTH_PASSWORD"]
    app.config["BASIC_AUTH_FORCE"] = True
    basic_auth = BasicAuth(app)


@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/query/points", methods=["POST"])
def api_query_points():

    ft = json.loads(request.form["feature"])
    continent = ft["properties"]["continent"]
    geom = geometry.shape(ft["geometry"])

    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    print ('geom',geometry.mapping(ops.transform(wgs2web,geom)))

    query = session.query(OSMPoint).filter(OSMPoint.way.ST_Intersects(from_shape(ops.transform(wgs2web,geom), srid=3857)))

    result = query.all()

    results_json = []

    for ii_r, r in enumerate(result):
        print ('r',r)

        res_dict = {kk:r.__getattribute__(kk) for kk in dir(OSMPoint) if not (kk.startswith('_') or kk=='metadata' or kk=='way') and r.__getattribute__(kk) is not None}
        res_dict['geometry'] = str(r.way)

        results_json.append(res_dict)

    results_json = {"points": results_json}

    print ('results_json',results_json)

    return jsonify(results_json)

@app.route("/query/lines", methods=["POST"])
def api_query_lines():

    ft = json.loads(request.form["feature"])
    continent = ft["properties"]["continent"]
    geom = geometry.shape(ft["geometry"])

    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    print ('geom',geometry.mapping(ops.transform(wgs2web,geom)))

    query = session.query(OSMLine).filter(OSMLine.way.ST_Intersects(from_shape(ops.transform(wgs2web,geom), srid=3857)))

    result = query.all()

    results_json = []

    for ii_r, r in enumerate(result):
        print ('r',r)

        res_dict = {kk:r.__getattribute__(kk) for kk in dir(OSMLine) if not (kk.startswith('_') or kk=='metadata' or kk=='way') and r.__getattribute__(kk) is not None}
        res_dict['geometry'] = str(r.way)

        results_json.append(res_dict)

    results_json = {"lines": results_json}

    print ('results_json',results_json)

    return jsonify(results_json)

@app.route("/query/polygons", methods=["POST"])
def api_query_polygons():

    ft = json.loads(request.form["feature"])
    continent = ft["properties"]["continent"]
    geom = geometry.shape(ft["geometry"])

    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    print ('geom',geometry.mapping(ops.transform(wgs2web,geom)))

    query = session.query(OSMPolygon).filter(OSMPolygon.way.ST_Intersects(from_shape(ops.transform(wgs2web,geom), srid=3857)))

    result = query.all()

    results_json = []

    for ii_r, r in enumerate(result):
        print ('r',r)
        res_dict = {}
        res_dict['properties'] = {kk:r.__getattribute__(kk) for kk in dir(OSMPolygon) if not (kk.startswith('_') or kk=='metadata' or kk=='way') and r.__getattribute__(kk) is not None}
        res_dict['geometry'] = str(r.way)

        results_json.append(res_dict)

    results_json = {"polygons": results_json}

    print ('results_json',results_json)

    return jsonify(results_json)


if __name__ =="__main__":
    app.run(host="0.0.0.0")
