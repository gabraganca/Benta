"""
Test function from the astronomy module.
"""
import numpy as np
from benta.astronomy import helio2galactic

def test_helio2galactic():
    """Make basic test of the `helio2galactic` function.

    It tests the case of a object located 1 kpc from the Sun in the direction
    of the Galactic anticenter. It does not test error.
    """
    gal_l, gal_lon, helio_distance, gal_dist = 180, 0, 1, 9.33

    result = helio2galactic(gal_l, gal_lon, helio_distance)

    assert isinstance(result, float)
    assert np.allclose(result, gal_dist)
