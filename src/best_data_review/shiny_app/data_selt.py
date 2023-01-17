# data_selt.py


import logging
import pandas as pd
import numpy as np
from shiny import ui, req, reactive, module

log = logging.getLogger("best_app")


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
        'args': list
            One timestamp, value to mark as selected.
        'kwargs': dict
            Contains keys:
                `min`: minimum of `timestamp` values
                `max`: maximum of `timestamp` values
    """
    dt1 = dta.index.min().floor('D')
    dtend = dta.index.max().ceil('D')
    return {
        'args': [dt1]
        , 'kwargs': {
            'min': dt1
            , 'max': dtend}}


def data_select(
    dta: pd.DataFrame
    , dt_start: pd.Timestamp
    , days: int
) -> pd.DataFrame:
    """Implement time range selection."""
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
def create_ui():
    """Build user interface for data_review1.

    Returns
    -------
    _type_
        _description_
    """
    return ui.TagList(
        ui.input_date(
            'dt_start'
            , 'Start Date'
            , value='2021-08-03')
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
    @reactive.Effect()
    def _dt_start():
        req(dtar)
        dta = dtar()
        ddparms = calc_default_date_parms(dtar())
        log.debug(f"Executing dta_selt._dt_start++++++++++++++{ddparms}")
        ui.update_date(
            'dt_start'
            , **ddparms['kwargs'])

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
