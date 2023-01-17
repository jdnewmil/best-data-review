# irradiance.py
"""Bifacial irradiance calculations."""

import numpy as np
import pandas as pd
import best_data_review.bifi_calcs.geometry as bgeom


def calc_outboard_sat_sensor_weight(
    sun_az: pd.Series
    , sun_el: pd.Series
    , height: float
    , offset: float
) -> pd.DataFrame:
    """Model single-axis-tracker outboard sensor.

    Parameters
    ----------
    sun_az : pd.Series
        Azimuth coordinate of sun (radians; 0=north, pi/2=East)
    sun_el : pd.Series
        Apparent elevation coordinate of sun (radians; 0=horizon, pi/2=zenith)
    height : float
        Height of bottom of array south edge (m)
    offset : float
        Horizontal offset of sensor from shade-casting edge of array (m)

    Returns
    -------
    pd.DataFrame
        Calculation results, including columns:
        phi : float
            Shade angle along tracker axis (radians; 0=horizontal)
        psi : float
            Angle between sensor and shade line along tracker axis,
            smaller than phi when mounted at south end of tracker.
            (radians)
        phi_deg : float
            Degrees equivalent of phi.
        psi_deg : float
            Degrees equivalent of psi.
        W0 : float
            Weighting factor assuming offset is zero (unitless)
        W : float
            Weighting factor assuming specified offset (unitless)
    """
    dta = pd.DataFrame({'phi': np.acos(bgeom.calc_cosphi(sun_az, sun_el))})
    dta = dta.assign(
        psi=bgeom.calc_psi(
            phi=dta['phi']
            , height=height
            , offset=offset)
        , phi_deg=np.rad2deg(dta['phi'])
        , psi_deg=np.rad2deg(dta['psi'])
        , W0=bgeom.calc_W(dta['phi'])
        , W=bgeom.calc_W(dta['psi']))
    return dta


def calc_outboard_sat_sensor_irr_pvsyst(
    W: np.array
    , GlobGnd: np.array
    , GlobHor: np.array
    , DifHor: np.array
    , albedo_near: np.array
    , Alb_Inc: np.array
    , GCR: float
    , BkVFLss: np.array
    , BmIncBk: np.array
    , GlobBak: np.array
) -> pd.DataFrame:
    dta = pd.DataFrame({
        'E_sky_rear': W * DifHor
        , 'E_gnd_rear': (
            W * (GlobGnd * albedo_near - Alb_Inc)
            + (1 - W) * (GlobGnd * albedo_near / GCR - BkVFLss))})
    return dta.assign(
        E_rear_calc=dta['E_gnd_rear'] + dta['E_sky_rear'] + BmIncBk
        , odd=dta['E_rear_calc'] < GlobBak
        , G1=(GlobHor * albedo_near - Alb_Inc)
        , G2=(GlobGnd * albedo_near / GCR - BkVFLss))
