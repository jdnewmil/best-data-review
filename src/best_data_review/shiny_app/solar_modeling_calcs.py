"""Solar modeling functions."""

import pandas as pd
import numpy as np
import pvlib


def add_solar_geometry(
    dta: pd.DataFrame
    , site_info: pd.Series
) -> pd.DataFrame:
    """Augment dta with calculated solar position columns.

    Parameters
    ----------
    dta : pd.DataFrame
        Dataframe with timezone-aware DatetimeIndex at beginning of
        interval. Timestamps are assumed to be at regular intervals.
    site_info : pd.Series
        Series of site parameters including:

    Returns
    -------
    pd.DataFrame
        `dta` argument augmented with additional columns:
        dtm_mid: pd.Timestamp

    """
    daily_albedo = (
        dta[['albedo', 'SRRL_albedo']]
        .loc[dta.index.hour.isin([11, 12, 13])]
        .resample('D')
        .agg(np.median)
        .fillna(method='ffill')
        .rename(columns={
            'albedo': 'daily_albedo'
            , 'SRRL_albedo': 'daily_SRRL_albedo'})
        .assign(
            daily_albedo=lambda df:
                df['daily_albedo']
                .where(
                    df['daily_albedo']
                    .lt(1)
                    , np.nan)
            , daily_SRRL_albedo=lambda df:
                df['daily_SRRL_albedo']
                .where(
                    df['daily_SRRL_albedo']
                    .lt(1)
                    , np.nan)))
    ans = dta.copy()
    ans['dtm_mid'] = ans.index + pd.Timedelta(seconds=30)
    ans['date'] = ans['dtm_mid'].dt.floor('D')
    ans = ans.merge(daily_albedo, left_on='date', right_index=True)
    solpos = pvlib.solarposition.get_solarposition(
        time=ans['dtm_mid']
        , latitude=site_info['latitude']
        , longitude=site_info['longitude']
        , altitude=site_info['elevation'])
    ans[['solar_apparent_zenith', 'solar_azimuth']] = (
        solpos[['apparent_zenith', 'azimuth']].values)
    ans['dni_extra'] = pvlib.irradiance.get_extra_radiation(
        datetime_or_doy=ans['dtm_mid'].dt.day_of_year)
    return ans


def add_array_irradiance(
    dta: pd.DataFrame
    , sys_info: pd.DataFrame
) -> pd.DataFrame:
    """Augment data with computed tracker position and irradiance.

    Parameters
    ----------
    dta : pd.DataFrame
        Data frame containing at least columns:
        solar_apparent_zenith : float
            Apparent zenith angle (degrees, 0-180)
        solar_azimuth : float
            Azimuth angle (degrees, 0=North, 90=East)
        row7tracker_angle : float
            Tilt angle (signed) of row7 (degrees, horizontal=0,
            toward EAST positive)
        SRRL_GHI : float
            Global horizontal irradiance estimate fromm SRRL (W/m2)
        SRRL_DHI : float
            Diffuse horizontal irradiance estimate from SRRL (W/m2)
        SRRL_DNI : float
            Direct normal irradiance estimate from SRRL (W/m2)
        daily_albedo : float
            Estimated albedo of ground, presumably updated each day
        dni_extra : float
            Extraterrestrial (estimated) DNI (W/m2)

    sys_info : pd.DataFrame
        System information, indexed by site and subsystem,
        with at least columns:
        max_tilt : float
            Maximum tilt slope allowed by design (degrees from horizontal).
        gcr : float
            Ground cover ratio, fraction 0-1.

    Returns
    -------
    pd.DataFrame
        `dta` dataframe augmented with additional columns:
        modeled_row7tracker_theta : float
            Modeled tracker rotation angle with negative
            to east. (degrees)
        modeled_row7aoi : float
            Sun angle of incidence on the tracker surface.
            (degrees)
        modeled_row7tracker_azimuth : float
            Apparent tracker tilt azimuth (degrees, 90 or 270)
        modeled_row7tracker_tilt : float
            Tracker effective tilt (always positive)
            (degrees; 0 is horizontal, 90 pointing at horizon)
    """
    dta[
        [
            'modeled_row7tracker_theta'
            , 'modeled_row7aoi'
            , 'modeled_row7tracker_azimuth'
            , 'modeled_row7tracker_tilt']
    ] = (
        pvlib.tracking.singleaxis(
            apparent_zenith=dta['solar_apparent_zenith']
            , apparent_azimuth=dta['solar_azimuth']
            , axis_tilt=0
            , axis_azimuth=180
            , max_angle=sys_info.loc[('BEST', 'row7'), 'max_tilt']
            , backtrack=True
            , gcr=sys_info.loc[('BEST', 'row7'), 'gcr']))
    dta['modeled_Gfront_row7pos'] = (
        pvlib.irradiance.get_total_irradiance(
            surface_tilt=dta['row7tracker_angle'].abs()
            , surface_azimuth=np.where(
                dta['row7tracker_angle'].lt(0.0)
                , 270  # data uses east as positive
                , 90)
            , solar_azimuth=dta['solar_azimuth']
            , solar_zenith=dta['solar_apparent_zenith']
            , ghi=dta['SRRL_GHI']
            , dhi=dta['SRRL_DHI']
            , dni=dta['SRRL_DNI']
            , albedo=dta['daily_albedo']
            , model='perez'
            , dni_extra=dta['dni_extra']))['poa_global']
    return dta
