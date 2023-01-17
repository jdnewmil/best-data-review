"""data_review1
"""
import logging
import pandas as pd
from plotnine import ggplot, aes, geom_point, theme_set \
    , theme_minimal, theme, element_text, xlab, facet_wrap
from shiny import ui, req, reactive, module, render

theme_set(theme_minimal())
log = logging.getLogger("best_app")


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


@module.ui
def create_ui() -> ui.TagList:
    """Build user interface for data_review1.

    Returns
    -------
    ui.TagList
        HTML user interface
    """
    return ui.TagList(
        ui.output_plot("line_plot1"))

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

    @output(id="line_plot1") # decorator to link this function to the "line_plot1" id in the UI
    @render.plot # a decorator to indicate we want the plot renderer
    def line_plot1():
        log.debug("Executing data_review1.line_plot1++++++++++++++")
        sub = dtalr()
        dta_info = dta_infor()  # extract data frame from reactive
        sub1 = pd.merge(
            sub
            , dta_info
            , left_on='variable'
            , right_on='col_names')
        plot = create_plot(sub1) # create our plot
        return plot  # and return it
