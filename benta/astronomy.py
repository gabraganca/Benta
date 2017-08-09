"""Main astronomy functions
"""
import numpy as np
from uncertainties import ufloat
from uncertainties.core import AffineScalarFunc

def helio2galactic(gal_lon, gal_lat, helio_dist,
                   sun_dist=(8.33, 0.35)):
    """Converts heliocentric distance to Galactocentric Distance.

    If an error is given for the heliocentric distance, it also returns the
    error of the Galactocentric distance.

    Parameters
    ----------

    gal_lon: float
        Galactic longitude in degrees
    gal_lat: float
        Galactic latitude in degrees
    helio_dist: float, tuple
        Heliocentric distance of the object in parsecs. If the distance has an
        error associated, this variable can be passed as a tuple, i.e.,
        `(distance, error)`
    sun_dist: float, tuple, optional
        Galactocentric distance of the Sun. Default is from Gillessen et al
        (2009). A error for the solar disctane should be given if an error was
        provided for the heliocentric distance of the object.

    Returns
    -------

    float, tuple
        Object Galactocentric distance. If the error on the heliocentric
        distance was also given, it also returns the error on the
        Galactocentric distance.
    """
    if isinstance(helio_dist, tuple):
        # object distance plus error
        helio_dist = ufloat(helio_dist)

        try:
            # Sun distance plus error
            sun_dist = ufloat((sun_dist))
        except AttributeError:
            raise AttributeError("The error of the Sun's distance should "+\
                                 "also be included")

    else:
        # The error on the object distance will be not calculated.
        # We don't need the error on Sun's distance.
        try:
            sun_dist = sun_dist[0]
        except TypeError:
            #The distance was passed as int/float
            pass

    # Convert coordinates from degrees to radian
    gal_lon, gal_lat = np.deg2rad([gal_lon, gal_lat])


    galaxy_dist = ((helio_dist*np.cos(gal_lat))**2 + \
                    sun_dist**2 - \
                    2*helio_dist*np.cos(gal_lat)*sun_dist*np.cos(gal_lon))**0.5

    if isinstance(helio_dist, AffineScalarFunc):
        return galaxy_dist.n, galaxy_dist.s
    else:
        return galaxy_dist
