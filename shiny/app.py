# test.py

#import datetime
import pandas as pd
import data_review1
from shiny import App, ui, reactive

# global data for review
dta = pd.read_parquet('data/cache/dta.parquet')
dta.index.name = 'timestamp'
dta.reset_index(inplace=True)
dta_info = pd.read_csv('data/config/best_dta_col_info.csv')


def create_ui(dta: pd.DataFrame, dta_info: pd.DataFrame):
    """Top level UI factory.

    Parameters
    ----------
    dta : list
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # create our ui object
    app_ui = ui.page_fluid(
        data_review1.create_ui('first', dta, dta_info)
    )
    return app_ui


# wrapper function for the server, allows the data
# to be passed in
def create_server(dta: pd.DataFrame) -> callable:
    """Top level server factory

    Parameters
    ----------
    dta : pd.DataFrame
        Dataframe to review in server
    """
    def server(input, output, session):
        dtar = reactive.Value(dta)
        dta_infor = reactive.Value(dta_info)
        data_review1.server('first', dtar, dta_infor)

    return server

# a ui is effectively an html page
frontend = create_ui(dta, dta_info)
# a server is a callable (function) invoked when
# the html widgets send messages back
myserver = create_server(dta)
app = App(frontend, myserver)
