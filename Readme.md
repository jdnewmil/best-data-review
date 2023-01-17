Readme
======

This repo contains a [shiny-python](https://shiny.rstudio.com/py/) app to review solar irradiance
data collected from the National Renewable Energy Laboratory Bifacial Experimental Single-Axis Tracking ([BEST](https://datahub.duramat.org/project/about/nrel-bifacial-experimental-single-axis-tracking-field))photovoltaic power array.

## Prep for using the app

Prepare a virtual Python environment based on the supplied `requirements.txt`. This app was developed using a `conda` virtual environment named `best`, but a `venv` could possibly be used instead.

```bash
conda env create -f environment.yml
# or
# pip install -r requirements.txt 
```

The `src` directory contains the shiny app and supporting python code as a package that needs to be linked into the virtual environment. 

```bash
conda activate best
pip install --no-deps -e src
```

## Download data to review

The `data` directory in the top-level project directory contains the core configuration files that will be used by the app.

The `src/best_data_review/prep1.py` script downloads four csv files into `data/raw` as csv files and combines them into one `data/cache/dta.parquet` file. It can be invoked from the commandline once the package is installed:

```bash
best-prep1  # invokes the prep1.py script for you
# from the top level directory of this repository
# python src/best_data_review/prep1.py  #
```

## Invoke the app

```bash
best-app
# from the top level directory of this repository
# shiny run --host localhost --port 5000 --launch-browser shiny/app.py
```

The app will open a web page to support user interactions, and remain active to support actions triggered through that web page. Ctrl-C can be used in the command window to stop serving the app. Once the server has stopped, the browser tab will become disabled, and the user must close it.

