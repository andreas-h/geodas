# -*- coding: utf-8 -*-
"""
*****************************************************************************
geodas - Geospatial Data Analysis in Python
*****************************************************************************

:Author:    Andreas Hilboll <andreas@hilboll.de>
:Date:      Mon Jan 21 19:52:07 2013
:Website:   http://andreas-h.github.com/geodas/
:License:   GPLv3
:Version:   0.1
:Copyright: (c) 2012-2013 Andreas Hilboll <andreas@hilboll.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""

# Library imports
# ============================================================================

from collections import OrderedDict

import numpy as np


# Definition of the ``coordinateset`` class
# ============================================================================

class coordinateset(object):
    """Base class for a collection of all coordinates of a data variable

    """


# Initialization of the ``coordinateset`` class
# ----------------------------------------------------------------------------

    def __init__(self, ):
        """
        Parameters
        ----------

        """


# Definition of the ``coordinate`` class
# ============================================================================

class coordinate(object):
    """Base class for a coordinate variable

    Currently, the ``coordinate`` class is just a wrapper around
    ``numpy.ndarray``, with some additional attributes. It doesn't *do*
    anything yet.

    Parameters
    ----------
    data : numpy.ndarray

    name : str

    unit : str

    centered : bool

    """

# Initialization of the ``coordinate`` class
# ----------------------------------------------------------------------------

    def __init__(self, data, name, units, centered=True):
        """

        """
        # TODO: Sanity-checks
        self._data = data
        self.name = name
        self.units = units
        self._centered = centered


# Find the indices for slicing two coordinates to a common covered range
# ============================================================================

def get_common_range(coordinates):
    """Get indices to slice ``coordinate`` objects to a common range

    coordinates : tuple of geodas.core.coordinate

    """
    mins = [min(t) for t in coordinates]


def _array_get_common_range_index(arrays):
    """Get indices to slice sorted arrays to a common range"""
    mins = [np.min(t) for t in arrays]
    maxs = [np.max(t) for t in arrays]
    lower_bound = np.max(mins)
    upper_bound = np.min(maxs)
    lower_row = [np.searchsorted(arr, lower_bound, side='left') for arr in arrays]
    upper_row = [np.searchsorted(arr, upper_bound, side='right') for arr in arrays]
    res = zip(lower_row, upper_row)
    return res
