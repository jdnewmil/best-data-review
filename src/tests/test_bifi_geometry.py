# test_bifi_geometry.py

import numpy as np
import pandas as pd
import pytest
import best_data_review.bifi_calcs.geometry as bgeom


def test_calc_cosphi():
    dta1 = pd.DataFrame({
        'sun_az': [np.pi, 2 * np.pi / 3]
        , 'sun_el': [np.pi / 6, np.pi / 6]})
    ans = bgeom.calc_cosphi(
        sun_az=dta1['sun_az']
        , sun_el=dta1['sun_el'])
    assert np.allclose(ans, [0.8660254, 0.4330127])

psi_trials = [
    (1.5, 1., (0.39498093, 1.4817163))
    , (1.5, -1., (0.7537516, 2.46451003))]

@pytest.mark.parametrize(
    "height,offset,expected"
    , psi_trials)
def test_calc_psi(height, offset, expected):
    """Test calc_psi."""
    dta1 = pd.DataFrame(dict(
        phi=[np.pi / 6, 2 * np.pi / 3]))
    ans = bgeom.calc_psi(
        phi=dta1['phi']
        , height=height
        , offset=offset)
    assert np.allclose(ans, expected)


@pytest.mark.parametrize(
    "height,offset,expected"
    , psi_trials)
def test_calc_psi_alt(height, offset, expected):
    """Test calc_psi."""
    dta1 = pd.DataFrame(dict(
        phi=[np.pi / 6, 2 * np.pi / 3]))
    ans = bgeom.calc_psi_alt(
        phi=dta1['phi']
        , H=height
        , L=offset)
    assert np.allclose(ans, expected)
