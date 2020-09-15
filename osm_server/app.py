from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely import geometry

from osm_server.utils import wgs2web
from osm_server.models import OSMLine, OSMRoads, OSMPolygon, OSMPoint

if "BASIC_AUTH_USERNAME" in os.environ:
    app.config["BASIC_AUTH_USERNAME"] = os.environ["BASIC_AUTH_USERNAME"]
    app.config["BASIC_AUTH_PASSWORD"] = os.environ["BASIC_AUTH_PASSWORD"]
    app.config["BASIC_AUTH_FORCE"] = True
    basic_auth = BasicAuth(app)


app = Flask(__name__)

@api.route("/query/points")
def api_query_points():
    ft = request.args.get("feature")
    continent = ft["properties"]["continent"]
    geom = geometry.shape(ft["geometry"])

    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    query = session.query(OSMPoint).filter(OSMPoint.way.ST_Intersects(from_shape(wgs2web(geom), srid=3857)))

    result = query.all()

    results_json = []

    for r in result:
        results_json.append(
            {kk:r.__getattribute__(kk) for kk in dir(OSMPoint) if not kk.startswith('_') and r.__getattribute__(kk) is not None})

    results_json = {"points": results_json}

    return jsonify(results_json)