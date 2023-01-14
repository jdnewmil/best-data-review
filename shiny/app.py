# test.py

#import datetime
import pathlib
import pandas as pd
import data_review1
import data_sel     # variable selection
import data_selt    # time selection
import data_any1
import solar_modeling_calcs as smc
from shiny import App, ui, reactive, render


prjdir = pathlib.Path(__file__).parent.parent
dtadir = prjdir / 'data'
cfgdir = dtadir / 'config'
cachedir = dtadir / 'cache'

# global data for review
dta = pd.read_parquet(cachedir / 'dta.parquet')
dta.index.name = 'timestamp'
dta_info = pd.read_csv(cfgdir / 'best_dta_col_info.csv')
site_info = pd.read_csv(
    cfgdir / 'site_info.csv'
    , index_col=0
    ).loc['BEST', :]
sys_info = pd.read_csv(
    cfgdir / 'sys_info.csv'
    , index_col=[0, 1])


def create_ui(dta: pd.DataFrame, dta_info: pd.DataFrame):
    """Top level UI factory.

    Parameters
    ----------
    dta : pd.DataFrame
        Datetime-indexed data frame of time-series data
    dta_info : pd.DataFrame
        Dataframe of descriptive categories for columns in
        `dta`.

    Returns
    -------
    list
        List of HTML text strings defining the web page that will
        be managed with the server.
    """
    # create our ui object
    app_ui = ui.page_fluid(
        ui.panel_title("BEST Data Review")
        , ui.navset_tab_card(
            ui.nav(
                'Preview'
                # upper pane (selection controls)
                , ui.row(
                    ui.column(
                        4
                        , data_sel.create_ui(id='main', dta=dta, dta_info=dta_info))
                    , ui.column(1)
                    , ui.column(
                        3
                        , *[data_selt.create_ui(id='main', dta=dta)]))
                # lower pane (tabbed displays)
                , ui.navset_tab_card(
                    ui.nav(
                        'Trend'
                        , data_review1.create_ui(id='first'))
                    , ui.nav(
                        'Data Availability'
                        , data_any1.create_ui(id='data_any_plot'))
                    , ui.nav(
                        'Site Info'
                        , ui.output_table(id='rendered_site_info'))
                    , ui.nav(
                        'System Info'
                        , ui.output_table(id='rendered_sys_info'))))))
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

    Returns
    -------
    callable
        Function to respond to web page activity.
    """
    def server(input, output, session):
        dtar = reactive.Value(dta)
        dta_infor = reactive.Value(dta_info)
        dta_selt_raw_r = data_selt.server('main', dtar)  # time filter

        @reactive.Calc
        def dta_seltr():
            """Add computed columns to selected dataset.

            Returns
            -------
            pd.DataFrame
                see `smc.add_solar_geometry` and `smc.add_array_irradiance`.
            """
            dta_selt_raw = dta_selt_raw_r()
            dtasel = smc.add_solar_geometry(dta_selt_raw, site_info=site_info)
            dtasel = smc.add_array_irradiance(dtasel, sys_info=sys_info)
            return dtasel

        dta_sel_r = data_sel.server('main', dta_seltr, dta_infor)  # variables filter

        @reactive.Calc
        def dtalr():
            """Long-shaped reactive data function.

            Returns
            -------
            pd.DataFrame
                Contains columns:
                timestamp: datetime[ns]
                variable: str
                    Name of parameter
                value: float
                    Value of parameter
            """
            dta_sel1 = dta_sel_r()
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
            , dta_selr=dta_sel_r)

        @output()
        @render.table(index=True)
        def rendered_site_info():
            return pd.DataFrame({
                'BEST' : site_info}).T

        @output()
        @render.table(index=True)
        def rendered_sys_info():
            return sys_info

    return server

# a ui is effectively an html page
frontend = create_ui(dta, dta_info)
# a server is a callable (function) invoked when
# the html widgets send messages back
myserver = create_server(dta, dta_info)
app = App(frontend, myserver)
