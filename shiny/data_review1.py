"""data_review1
"""

import pandas as pd
from plotnine import ggplot, aes, geom_point, theme_set \
    , theme_minimal, theme, element_text, xlab, facet_wrap
from shiny import ui, req, reactive, module, render

theme_set(theme_minimal())


def calc_default_date_parms(dta: pd.DataFrame) -> dict:
    """Identify a default date interval

    Parameters
    ----------
    dta : pd.DataFrame
        DataFrame containing at least a `timestamp` column.

    Returns
    -------
    dict
        Must contain keys:
        `min`: minimum of `timestamp` values
        `max`: maximum of `timestamp` values
        `value`: default value (=min)
    """
    dt1 = min(dta['timestamp']).floor('D')
    dtend = max(dta['timestamp']).ceil('D')
    return {
        'min': dt1
        , 'max': dtend
        , 'value': dt1}


# utility function to draw a scatter plot
def create_plot(data):
    """Plot long dataset.

    Parameters
    ----------
    data : pd.DataFrame
        Long data frame with columns:
        timestamp:

    Returns
    -------
    _type_
        ggplot object rendered for delivery to UI.
    """
    req(0<len(data))
    print(data)
    plot = (
        ggplot(
            data
            , aes(
                x = 'timestamp'
                , y='value'
                , color='variable'))
        + geom_point(size=0.5)
        + xlab('Time')
        + facet_wrap('~unit', ncol=1, scales="free_y")
        + theme(axis_text_x=element_text(
            ha='right'
            , va='top'
            , rotation=30)))
    return plot.draw()


def subset_review1(
    dta: pd.DataFrame
    , variables: list
    , dt_start: pd.Timestamp
    , days: int
) -> pd.DataFrame:
    dt1 = (
        dt_start
        .tz_localize(dta['timestamp'].dt.tz))
    dt2 = dt1 + pd.Timedelta(
        value=days
        , unit='D')
    dtal0 = (
        dta
        .loc[
            dta['timestamp'].gt(dt1)
            & dta['timestamp'].le(dt2)
            , ['timestamp'] + variables]
        .melt(
            id_vars=['timestamp']
            , var_name='variable'
            , value_name='value')
        .dropna())
    return dtal0


def agg_has_non_na(dta: pd.DataFrame, variables: list) -> pd.DataFrame:
    """Aggregate True if any non-nan data by day.

    Parameters
    ----------
    dta : pd.DataFrame
        Data frame with time index (wide)
    variables: list of str
        Names of variables of interest

    Returns
    -------
    pd.DataFrame
        Long daily data frame
        timestamp: Beginning of day
        variable: list of names of variables
        value: True if any non-nan data in this day
    """
    has_non_na = lambda x: np.any(x.isna())
    dtal_non_na = (
        dta.loc[:, variables]
        .resample('D')
        .agg(has_non_na)
        .reset_index()
        .melt(
            id_vars=['timestamp']
            , var_name='variable'
            , value_name='value'))
    return dtal_non_na


@module.ui
def create_ui(dta: pd.DataFrame, dta_info: pd.DataFrame):
    """Build user interface for data_review1

    Parameters
    ----------
    dtal : pd.DataFrame
        Time series data, in long format:
        `timestamp`: pd.Timeseries
        `variables`: str
        `value`: float
    dta_info : pd.DataFrame
        Definitions of variables defined in

    Returns
    -------
    _type_
        _description_
    """
    choices = dta_info['col_names']
    return ui.na(
        ui.row(
        ui.column(
            4
            , offset=1
            , *[
                # an input widget that allows us to select multiple values
                # from the set of choices
                ui.input_select(
                    "variables"
                    , "Variable"
                    , choices=list(choices)
                    , multiple=True
                    , size=6)])
        , ui.column(1)
        , ui.column(
            3
            , ui.input_date(
                'dt_start'
                , 'Start Date'
                , **calc_default_date_parms(dta)))
        , ui.column(
            3
            , ui.input_numeric(
                'days'
                , 'Days'
                , value=7
                , step=1
                , min=1
                , max=366
                )))
        , ui.row(
            ui.column(
                12
                # an output container in which to render a plot
                , ui.output_plot("plot1"))))

@module.server
def server(
    input
    , output
    , session
    , dtar: reactive
    , dta_infor: reactive
):
    """Server definition for data_review1 module.
    """
    @reactive.Calc
    def dtal():
        req(input.variables())
        req(input.dt_start())
        req(input.days())
        #req(dtar())
        dta = dtar()
        variables = list(input.variables())
        dt_start1 = pd.to_datetime(input.dt_start())
        days1 = input.days()
        # transform from wide to long-filtered
        dtal0 = subset_review1(
            dta
            , variables=variables
            , dt_start=dt_start1
            , days=days1)
        print(dtal0)
        return dtal0

    @output(id="plot1") # decorator to link this function to the "plot1" id in the UI
    @render.plot # a decorator to indicate we want the plot renderer
    def plot_dtal():
        sub = dtal()
        dta_info = dta_infor()  # extract data frame from reactive
        sub1 = pd.merge(
            sub
            , dta_info
            , left_on = 'variable'
            , right_on= 'col_names'
        )
        # sub = sub[sub['variable'].isin(vars)] # use it to create a subset
        plot = create_plot(sub1) # create our plot
        return plot # and return it
