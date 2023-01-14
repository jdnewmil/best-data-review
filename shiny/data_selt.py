# data_selt.py

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
    , dt_start: pd.Timestamp
    , days: int
) -> pd.DataFrame:
    if days is None:
        selected = dta
    else:
        dt1 = (
            dt_start
            .tz_localize(dta.index.tz))
        dt2 = dt1 + pd.Timedelta(value=days, unit='D')
        row_bool = np.logical_and(
            dt1 <= dta.index
            , dta.index <= dt2)
        selected = dta.loc[row_bool, :]
    return selected


@module.ui
def create_ui(dta: pd.DataFrame):
    """Build user interface for data_review1

    Parameters
    ----------
    dta : pd.DataFrame
        Time series data, in wide format:
        `timestamp`: pd.Timeseries
        various column names : float

    Returns
    -------
    _type_
        _description_
    """
    return ui.TagList(
        ui.input_date(
            'dt_start'
            , 'Start Date'
            , **calc_default_date_parms(dta))
        , ui.input_numeric(
            'days'
            , 'Days'
            , value=7
            , step=1
            , min=1
            , max=366))


@module.server
def server(
    input
    , output
    , session
    , dtar: reactive
):
    """Server definition for data_review1 module."""
    @reactive.Calc
    def dta_selt():
        req(input.dt_start())
        dta = dtar()
        dt_start1 = pd.to_datetime(input.dt_start())
        days1 = input.days()
        if '' == days1:
            days1 = None
        # select rows by timestamp
        dta_selt = data_select(
            dta
            , dt_start=dt_start1
            , days=days1)
        return dta_selt

    return dta_selt
