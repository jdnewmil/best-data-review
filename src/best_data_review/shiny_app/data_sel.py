# data_sel.py

import logging
import pandas as pd
import numpy as np
from shiny import ui, req, reactive, module

log = logging.getLogger("best_app")


@module.ui
def create_ui():
    """Build user interface for data_review1.

    Returns
    -------
    _type_
        _description_
    """
    return ui.TagList(
        ui.input_select(
            "variables"
            , "Variable"
            , choices=[]
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
    """Server definition for data_review1 module."""
    @reactive.Effect
    def _variables():
        choices = dta_infor()['col_names'].to_list()
        log.debug(f"Executing dta_sel._variables++++++++++++++{choices}")
        ui.update_select(
            "variables"
            , choices=choices
            , session=session)

    @reactive.Calc
    def dta_sel():
        req(input.variables())
        dta = dtar()
        variables = list(input.variables())
        # select columns according to variables
        dta_sel = dta.loc[:, variables]
        return dta_sel

    return dta_sel
