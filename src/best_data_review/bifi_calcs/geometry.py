"""Solar modeling functions.
"""

import pandas as pd
import numpy as np
import pvlib


def calc_cosphi(sun_az: np.array, sun_el: np.array) -> np.array:
    """Compute cosine of shade angle from sun azimuth and elevation.

    Parameters
    ----------
    sun_az : np.array
        Sun azimuth (radians; 0=North, pi/2=East)
    sun_el : np.array
        Sun elevation (radians; 0=horizon, pi/2=zenith)

    Returns
    -------
    np.array
        Cosine of shade angle (unitless)
    """
    return -np.cos(sun_az) * np.cos(sun_el)


def calc_psi(phi: np.array, height: float, offset: float) -> np.array:
    """Compute angle between sensor and shade line assuming nonzero offset.

    Parameters
    ----------
    phi : np.array
        Shade angle relative to array edge along tracker axis
        (radians; 0=horizontal)
    height : float
        Height of bottom of array south edge (m)
    offset : float
        Horizontal offset of sensor from shade-casting edge of array (m)

    Returns
    -------
    np.array
        Computed shade angle between sensor and shade line (radians)
    """
    s_phi = np.sin(phi)
    return np.arctan2(
        height * s_phi
        , offset * s_phi + height * np.cos(phi))


def calc_psi_alt(phi: np.array, H: float, L: float) -> np.array:
    """Compute angle between sensor and shade line w nonzero offset (arccos).

    Parameters
    ----------
    phi : np.array or pd.Series
        Shade angle relative to array edge along tracker axis
        (radians; 0=horizontal)
    H : float
        Height of bottom of array south edge (m)
    L : float
        Horizontal offset of sensor from shade-casting edge of array (m)

    Returns
    -------
    np.array
        Computed shade angle between sensor and shade line (radians)
    """
    s_phi = np.sin(phi)
    c_phi = np.cos(phi)
    o_s_phi = L * s_phi
    h_c_phi = H * c_phi
    # h_s_phi = H * s_phi
    num = o_s_phi + h_c_phi
    den2 = (
        o_s_phi * o_s_phi
        + 2 * h_c_phi * o_s_phi
        + H * H)
    return np.arccos(num / np.sqrt(den2))


def calc_W(shadeangle: np.array) -> np.array:
    """Calculate W weight factor.

    Parameters
    ----------
    shadeangle : np.array
        Assumed angle of shade line with respect to equator-facing
        horizontal (radians).

    Returns
    -------
    np.array
        W weight factor.
    """
    return 0.5 * (1 + np.cos(shadeangle))


