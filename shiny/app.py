# test.py

#import datetime
import pandas as pd
import data_review1
import data_sel
import data_any1
from shiny import App, ui, reactive, render

# global data for review
dta = pd.read_parquet('data/cache/dta.parquet')
dta.index.name = 'timestamp'
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
        ui.panel_title("BEST Data Review")
        , ui.navset_tab_card(
            ui.nav(
                'Preview'
                , data_sel.create_ui(id='main', dta=dta, dta_info=dta_info)
                , ui.navset_tab_card(
                    ui.nav(
                        'Trend'
                        , data_review1.create_ui(id='first'))
                    , ui.nav(
                        'Data Availability'
                        , data_any1.create_ui(id='data_any_plot'))))))
    return app_ui


# wrapper function for the server, allows the data
# to be passed in
def create_server(
        dta: pd.DataFrame
        , dta_info: pd.DataFrame
    ) -> callable:
    """Top level server factory

    Parameters
    ----------
    dta : pd.DataFrame
        Dataframe to review in server
    """
    def server(input, output, session):
        dtar = reactive.Value(dta)
        dta_infor = reactive.Value(dta_info)
        dta_selr = data_sel.server('main', dtar, dta_infor)

        @reactive.Calc
        def dtalr():
            dta_sel1 = dta_selr()
            return (
                dta_sel1
                .reset_index()
                .melt(
                    id_vars=['timestamp']
                    , var_name='variable'
                    , value_name='value')
                .dropna())

        @output
        @render.text
        def test_dtal():
            dtal = dtalr()
            return f'dtal size = {dtal.size}'

        data_review1.server(
            'first'
            , dtalr=dtalr
            , dta_infor=dta_infor)
        data_any1.server(
            'data_any_plot'
            , dta_selr=dta_selr)

    return server

# a ui is effectively an html page
frontend = create_ui(dta, dta_info)
# a server is a callable (function) invoked when
# the html widgets send messages back
myserver = create_server(dta, dta_info)
app = App(frontend, myserver)
