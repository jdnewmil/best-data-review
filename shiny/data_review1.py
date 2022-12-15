"""data_review1
"""

import pandas as pd
from plotnine import ggplot, aes, geom_point, theme_set \
    , theme_minimal, theme, element_text, xlab, facet_wrap
from shiny import ui, req, reactive, module, render

theme_set(theme_minimal())


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
def create_ui():
    """Build user interface for data_review1

    Returns
    -------
    ui.page_fluid
        HTML user interface
    """
    return ui.row(
        ui.column(
            12
            # an output container in which to render a plot
            , ui.output_plot("line_plot1")))

@module.server
def server(
    input
    , output
    , session
    , dtalr: reactive
    , dta_infor: reactive
):
    """Server definition for data_review1 module.
    """

    @output(id="line_plot1") # decorator to link this function to the "plot1" id in the UI
    @render.plot # a decorator to indicate we want the plot renderer
    def plot_dtal():
        sub = dtalr()
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
