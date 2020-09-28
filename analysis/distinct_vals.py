import logging, json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from osm_server.models import OSMLine, OSMPolygon, OSMPoint

logger = logging.getLogger("analysis")
logger.setLevel(logging.DEBUG)

def get_distinct(continent):



    engine = create_engine(os.environ['DB_URI']+continent)
    session = sessionmaker(bind=engine)()

    all_results = {}

    for OSM_OBJ in [OSMLine, OSMPolygon, OSMPoint]:

        logger.info(f'Getting distinct vals for {continent}, {OSM_OBJ.__tablename__}.')

        all_results[OSM_OBJ.__tablename__] = {}

        attr_columns = {kk:vv for kk,vv in vars(OSM_OBJ).items() if not (kk.startswith('_') or kk=='metadata' or kk=='way')}

        for kk, vv in vars(OSM_OBJ).items():
            if not (kk.startswith('_') or kk=='metadata' or kk=='way'):
                logger.info(f'Querying {kk}...')
                Q = session.query(vv).distinct()
                res = Q.all()
                logger.info('res',res)
                all_results[OSM_OBJ.__tablename__][kk] = res

    json.dump(all_results, open(f'./distinct_{continent}.json'))


if __name__=="__main__":

    CONTINENTS = ["central-america","antactica"] #["central-america","antactica","oceania","asia","south-america","north-america","africa","europe"]

    for continent in CONTINENTS:
        get_distinct(continent)