"""data_any1.py
"""

import pandas as pd
import numpy as np
from plotnine import ggplot, aes, geom_tile, theme_set \
    , theme_minimal, scale_fill_manual, facet_grid, labs \
    , scale_x_discrete
from shiny import ui, req, reactive, module, render

theme_set(theme_minimal())


def agg_has_non_na(dta_sel: pd.DataFrame) -> pd.DataFrame:
    """Aggregate True if any non-nan data by day.

    Parameters
    ----------
    dta_sel : pd.DataFrame
        Data frame with time index (wide) and desired set of columns
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
    dtal_non_na = (
        dta_sel
        .resample('D')
        .agg(lambda x: ~np.all(x.isna()))
        .reset_index()
        .melt(
            id_vars=['timestamp']
            , var_name='variable'
            , value_name='value'))
    dtal_non_na['day'] = pd.Categorical(
        dtal_non_na['timestamp'].dt.day
            , categories=range(1, 32))
    dtal_non_na['month'] = pd.Categorical(
        dtal_non_na['timestamp'].dt.month
        , categories=range(1, 13))
    dtal_non_na['year'] = pd.Categorical(
        dtal_non_na['timestamp'].dt.year
        , categories=range(
            dtal_non_na['timestamp'].dt.year.min()
            , dtal_non_na['timestamp'].dt.year.max()+1))
    return dtal_non_na

# utility function to draw a scatter plot
def create_plot(dta_sel: pd.DataFrame):
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
    dtal_non_na = agg_has_non_na(dta_sel=dta_sel)
    plot = (
        ggplot(
            dtal_non_na
            , aes(
                x='day'
                , y='variable'
                , fill='value'))
        + geom_tile()
        + scale_x_discrete(breaks=[1, 10, 20, 30])
        + scale_fill_manual(values={
            False: 'red'
            , True: 'blue'})
        + facet_grid('year ~ month' )
        + labs(x='Day of Month'
            , title='Any non-missing data'))
    return plot.draw()


@module.ui
def create_ui() -> ui.TagList:
    """Build user interface for data_any1.

    Returns
    -------
    ui.TagList
        HTML user interface
    """
    return ui.TagList(
        ui.output_plot("any_plot1"))

@module.server
def server(
    input
    , output
    , session
    , dta_selr: reactive
):
    """Server definition for data_review1 module.
    """

    @output # decorator to link this function to the "any_plot1" id in the UI
    @render.plot # a decorator to indicate we want the plot renderer
    def any_plot1():
        req(0<len(dta_selr()))
        return create_plot(dta_sel=dta_selr())
