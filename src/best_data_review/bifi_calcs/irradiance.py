# irradiance.py
"""Bifacial irradiance calculations."""

import numpy as np
import pandas as pd
import best_data_review.bifi_calcs.geometry as bgeom


def calc_outboard_sat_sensor_weight(
    AzSol: pd.Series
    , HSol: pd.Series
    , height: float
    , offset: float
) -> pd.DataFrame:
    """Model single-axis-tracker outboard sensor.

    Parameters
    ----------
    AzSol : pd.Series
        PVsyst-convention azimuth coordinate of sun (deg; 0=South, 90=West)
    HSol : pd.Series
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
        W : float
            Weighting factor assuming specified offset (unitless)
    """
    dta = pd.DataFrame({
        'sun_az': np.deg2rad(AzSol + 180.)
        , 'sun_el': np.deg2rad(HSol)})
    dta = dta.assign(
        phi=lambda df: np.arccos(bgeom.calc_cosphi(df['sun_az'], df['sun_el']))
        , psi=lambda df: bgeom.calc_psi(
            phi=df['phi']
            , height=height
            , offset=offset)
        , phi_deg=lambda df: np.rad2deg(df['phi'])
        , psi_deg=lambda df: np.rad2deg(df['psi'])
        , W=lambda df: bgeom.calc_W(df['psi']))
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
    """Implement PVsyst outboard axial down-facing sensor estimation."""
    dta = pd.DataFrame({
        'E_sky_rear': W * DifHor
        , 'E_gnd_rear': (
            W * (GlobGnd * albedo_near - Alb_Inc)
            + (1 - W) * (GlobGnd * albedo_near / GCR - BkVFLss))})
    return dta.assign(
        E_rear_calc=lambda df: df['E_gnd_rear'] + df['E_sky_rear'] + BmIncBk
        , odd=lambda df: df['E_rear_calc'] < GlobBak
        , G1=(GlobHor * albedo_near - Alb_Inc)
        , G2=(GlobGnd * albedo_near / GCR - BkVFLss))
