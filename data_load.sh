osm2pgsql \
   -d <database_name>  \
   --create \
   --flat-nodes <your/data/path/>europe_nodes.cache \
   --slim  \
   -G  \
   --hstore  \
   --tag-transform-script  \
   ~/src/openstreetmap-carto/openstreetmap-carto.lua  \
   -C 16000 \
   --number-processes 16  \
   -S ~/src/openstreetmap-carto/openstreetmap-carto.style  \
   <your/data/path/>europe-latest.osm.pbf