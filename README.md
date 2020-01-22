# osm-labelcube-generator
___
A repository to generate land cover labelcubes from OpenStreetMap. The script parses OSM data obtained using overpy to create label cubes for further workstreams, e.g. machine learning semantic segmentation.

## Setup

Clone the repository, submitting username and password when prompted:

    git clone https://github.com/Lkruitwagen/osm-labelcube-generator.git

### Optional - Create a new environment

We recommend using [conda](https://docs.conda.io/en/latest/) for package and environment management. Open a command line shell. Create a new environment `osm-labelcube`:

    conda create -n osm-labelcube python=3.7

Activate the environment:

    conda activate osm-labelcube

Install git, pip, and jupyter if not already installed:

    conda install git pip jupyter

Change directory into the repository:

    cd osm-labelcube-generator

Install remaining package requirements using pip:

    pip install -r requirements.txt

## Repo Structure

[Notebooks](notebooks/) contains Jupyter notebooks:
- [Prototyping](notebooks/prototyping.ipynb)

[labelcube](labelcube/) contains scripts:
- [labelcube.py](labelcube/labelcube.py) LabelCube class for generating cubes

[json_zoo](osm-labelcube-generator/json_zoo/) contains the strategies:
- [demo.json](osm-labelcube-generator/json_zoo/demo.json)


