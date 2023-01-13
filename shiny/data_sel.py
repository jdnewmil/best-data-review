# data_sel.py

import pandas as pd
import numpy as np
from shiny import ui, req, reactive, module

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
    dt1 = dta.index.min().floor('D')
    dtend = dta.index.max().ceil('D')
    return {
        'min': dt1
        , 'max': dtend
        , 'value': dt1}


def data_select(
    dta: pd.DataFrame
    , variables: list
    , dt_start: pd.Timestamp
    , days: int
) -> pd.DataFrame:
    if days is None:
        selected = dta.loc[:, variables]
    else:
        dt1 = (
            dt_start
            .tz_localize(dta.index.tz))
        dt2 = dt1 + pd.Timedelta(value=days, unit='D')
        row_bool = np.logical_and(
            dt1 <= dta.index
            , dta.index <= dt2)
        selected = dta.loc[row_bool, variables]
        # selected = dta.loc[dt1:dt2, variables]
    return selected


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
    choices = dta_info['col_names'].to_list()
    return ui.row(
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
        req(input.dt_start())
        #req(input.days())
        #req(dtar())
        dta = dtar()
        variables = list(input.variables())
        dt_start1 = pd.to_datetime(input.dt_start())
        days1 = input.days()
        if '' == days1:
            days1 = None
        # transform from wide to long-filtered
        dta_sel = data_select(
            dta
            , variables=variables
            , dt_start=dt_start1
            , days=days1)
        return dta_sel

    return dta_sel