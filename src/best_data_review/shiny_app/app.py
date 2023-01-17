# test.py

#import datetime
import pathlib
import logging
import pandas as pd
import best_data_review.shiny_app.data_review1 as data_review1
import best_data_review.shiny_app.data_sel as data_sel     # variable selection
import best_data_review.shiny_app.data_selt as data_selt    # time selection
import best_data_review.shiny_app.data_any1 as data_any1
import best_data_review.shiny_app.solar_modeling_calcs as smc
from shiny import App, ui, reactive, render


prjdir = pathlib.Path('.')
dtadir = prjdir / 'data'
cfgdir = dtadir / 'config'
cachedir = dtadir / 'cache'
log = logging.getLogger("best_app")

def create_ui():
    """Top level UI factory.

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
                        , data_sel.create_ui(id='main'))
                    , ui.column(1)
                    , ui.column(
                        3
                        , *[data_selt.create_ui(id='main')]))
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
def create_server() -> callable:
    """Top level server factory.

    Returns
    -------
    callable
        Function to respond to web page activity.
    """
    def server(input, output, session):
        dta_fnamer = reactive.Value(cachedir / 'dta.parquet')
        dta_info_fnamer = reactive.Value(cfgdir / 'best_dta_col_info.csv')
        site_info_fnamer = reactive.Value(cfgdir / 'site_info.csv')
        sys_info_fnamer = reactive.Value(cfgdir / 'sys_info.csv')

        @reactive.file_reader(dta_fnamer)
        def dtar() -> pd.DataFrame:
            """Read BEST time series data."""
            log.debug("Executing dtar++++++++++++++")
            dta = pd.read_parquet(dta_fnamer())
            dta.index.name = 'timestamp'
            return dta

        @reactive.file_reader(dta_info_fnamer)
        def dta_infor() -> pd.DataFrame:
            """Read column info."""
            log.debug("Executing dta_infor++++++++++++++")
            return pd.read_csv(dta_info_fnamer())

        @reactive.file_reader(site_info_fnamer)
        def site_infor() -> pd.DataFrame:
            site_info = pd.read_csv(
                site_info_fnamer()
                , index_col=0
            ).loc['BEST', :]
            return site_info

        @reactive.file_reader(sys_info_fnamer)
        def sys_infor() -> pd.DataFrame:
            sys_info = pd.read_csv(
                sys_info_fnamer()
                , index_col=[0, 1])
            return sys_info

        dta_selt_raw_r = data_selt.server('main', dtar)  # time filter

        @reactive.Calc
        def dta_seltr():
            """Add computed columns to selected dataset.

            Returns
            -------
            pd.DataFrame
                see `smc.add_solar_geometry` and `smc.add_array_irradiance`.
            """
            log.debug("Executing dta_seltr++++++++++++++")
            dta_selt_raw = dta_selt_raw_r()
            site_info = site_infor()
            sys_info = sys_infor()
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
            log.debug("Executing dtalr++++++++++++++")
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
                'BEST' : site_infor()}).T

        @output()
        @render.table(index=True)
        def rendered_sys_info():
            return sys_infor()

    return server


def best_app():
    """Wrap app invocation."""
    # a ui is effectively an html page
    frontend = create_ui()
    # a server is a callable (function) invoked when
    # the html widgets send messages back
    myserver = create_server()
    return App(frontend, myserver)


if __name__ == '__main__':
    app = best_app()
