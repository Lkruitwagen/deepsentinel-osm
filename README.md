# osm-server
___
The repository serves OSM points, lines, and polygons using a flask app. Use this repo if you need higher bandwidth access to OSM data than the [overpass](https://overpass-turbo.eu/) enpoints can provide.

## Setup

Clone the repository, submitting username and password when prompted:

    git clone https://github.com/Lkruitwagen/osm-labelcube-generator.git

### Create a new environment

We recommend using [conda](https://docs.conda.io/en/latest/) for package and environment management. Open a command line shell. Create a new environment `osm-server`:

    conda create -n osm-server python=3.6

Activate the environment:

    conda activate osm-server

Install git and pip if not already installed:

    conda install git pip

Change directory into the repository:

    cd osm-server

Install remaining package requirements using pip:

    pip install -r requirements.txt


### Clone OSM

Follow the tile-server osm instructions [here](https://switch2osm.org/serving-tiles/manually-building-a-tile-server-18-04-lts/). I found it was very unclear how much memory was needed to clone the entire planet. After exploding a 256gb memory machine with the `planet-latest.osm.pbf` file I changed tactics to creating 8 different databases, each serving one continent's worth of osm data. The continent extracts can be downloaded [here](https://download.geofabrik.de/). 

I also provisioned a large SDD to hold all the data. I moved my postgresql database to the new disk using [these instructions](https://www.digitalocean.com/community/tutorials/how-to-move-a-postgresql-data-directory-to-a-new-location-on-ubuntu-18-04).

Following the `switch2osm` instructions, create a database for each continent:

    CREATE DATABASE <continent>;
    CREATE EXTENSION postgis;
    CREATE EXTENSION hstore;

When you load in the data it may complain that it can't find `hstore`. I solved this by changing the `hstore` schema to public:

    ALTER EXTENSION hstore SET SCHEMA "public";

I also had to fiddle extensively with my postgres settings. For reference, I've put the `.conf` file in this repo: [/postgres.conf]. You can use if it you change the data directory in line 41 and copy it to `/etc/postgres/12/main/postgresql.conf`.

For each continent extract, load the data in the osm using the data loader shell script, [/data_load.sh], adjusting paths, etc. as necessary:

    sh ./data_load.sh

Iterating though the continents, I found that the \~10gb osm.pbg files took about 10 hours to load with `osm2pgsql` and expanded in many times in size. Loading all the continents took about four days with 64gb RAM and 16 vCPUs. 

We'll only use the `planet-osm-point`, `planet-osm-polygon`, and `planet-osm-line` tables after this process. Any `node.cache` files can be deleted.

### Set up the Flask app

I serve osm data in json format using a Flask app with Nginx and Gunicorn. Follow these instructions [here](https://medium.com/analytics-vidhya/part-1-deploy-flask-app-anaconda-gunicorn-nginx-on-ubuntu-4524014451b), with the modifications below. The DigitalOcean [guides](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) are also very helpful.

To use your conda environment in your flask app, you'll need to specify the conda bin paths, and add any environment variables. Create a `.env` file in this repo:

    touch .env
    nano .env

Then add the environment variables that you need:

    PATH="<path/to/your/conda>/bin:<path/to/your/conda>/envs/osm-server/bin"
    DB_URI="postgresql://<your_psqluser>:<your_psqlpassword>@localhost/"
    BASIC_AUTH_USERNAME="<a_basicauth_user>"
    BASIC_AUTH_PASSWORD="<a_basicauth_password>"


In `/etc/systemd/system/<yourapp>.service` you'll need to adapt the gunicorn configuration: 

    [Unit]
    Description=Gunicorn instance to serve osm-server flask app
    After=network.target
    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=<path/to/repo/root>
    EnvironmentFile=<path/to/repo/root>.env
    ExecStart=<path/to/your/conda>/envs/osm/bin/gunicorn --bind 0.0.0.0:5000 osm$
    [Install]
    WantedBy=multi-user.target

In order to get Nginx to be able to listen at port 80, I also had to disable apache: 

    sudo systemctl disable apache2

Congrats! Your flask app is ready to serve you OSM features!


## Useage

Let's use Python, [requests](https://pypi.org/project/requests/), [geojson](https://pypi.org/project/geojson/), [shapely](https://pypi.org/project/Shapely/) to access some OSM features using our flask app.

    import requests, geojson, json
    from shapely import geometry, ops

    # make a point
    carfax = geometry.Point(-1.258305, 51.751906)

    # buffer the point to get a box
    bbox = geometry.box(*carfax.buffer(0.02).bounds)

    # Make it a geojson Feature with the continent name in the properties
    ft = geojson.Feature(geometry=bbox, properties={'continent':'europe'})

    # set your basicauth username and password
    U, P = "<your_basicauth_username>", "<your_basicauth_password>"

    # prepare the query, specifying geom_type
    url = "http://<your_IP>:5000/query"  
    body = {'feature':json.dumps(ft), 'geom_type':'polygons'} # where geometry_type is one of points, lines, or polygons

    # execute the query
    response = requests.post(url, body, auth=(U,P))
    osm_features = json.loads(response)['features']







