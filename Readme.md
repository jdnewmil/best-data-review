Readme
======

This repo contains a [shiny-python](https://shiny.rstudio.com/py/) app to review solar irradiance
data collected from the National Renewable Energy Laboratory Bifacial Experimental Single-Axis Tracking ([BEST](https://datahub.duramat.org/project/about/nrel-bifacial-experimental-single-axis-tracking-field))photovoltaic power array.

## Prep for using the app

Prepare a virtual Python environment based on the supplied `requirements.txt`. This app was developed using a `conda` virtual environment, but a `venv` could possibly be used instead.

```bash
# from the top level directory of this repository
python src/prep1.py  #
```

## Invoke the app

```bash
# from the top level directory of this repository
shiny --host localhost --port 5000 --launch-browser shiny/app
```

