# data_sel.py

import pandas as pd
import numpy as np
from shiny import ui, req, reactive, module


def data_select(
    dta: pd.DataFrame
    , variables: list
) -> pd.DataFrame:
    return dta.loc[:, variables]


@module.ui
def create_ui(dta: pd.DataFrame, dta_info: pd.DataFrame):
    """Build user interface for data_review1

    Parameters
    ----------
    dtal : pd.DataFrame
        Time series data, in wide format:
        `timestamp`: pd.Timeseries
        various column names : float
    dta_info : pd.DataFrame
        Definitions of variables defined in

    Returns
    -------
    _type_
        _description_
    """
    choices = dta_info['col_names'].to_list()
    return ui.TagList(
        ui.input_select(
            "variables"
            , "Variable"
            , choices=list(choices)
            , multiple=True
            , size=6))

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
    def dta_sel():
        req(input.variables())
        dta = dtar()
        variables = list(input.variables())
        # select columns according to variables
        dta_sel = dta.loc[:, variables]
        return dta_sel

    return dta_sel
