# -*- coding: utf-8 -*-
#
# geodas - Geospatial Data Analysis in Python
#
#:Author:    Andreas Hilboll <andreas@hilboll.de>
#:Date:      Tue Jan 22 10:56:08 2013
#:Website:   http://andreas-h.github.com/geodas/
#:License:   GPLv3
#:Version:   0.1
#:Copyright: (c) 2012-2013 Andreas Hilboll <andreas@hilboll.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Library imports
# ============================================================================

from collections import OrderedDict

import bottleneck as bn
import numpy as np
import numpy.ma as ma

from geodas.core.coordinate import CoordinateArray


# Definition of the ``dimension`` class
# ============================================================================

class gridded_array(object):
    """Base class for a gridded data array

    Parameters
    ----------
    data : numpy.ndarray

    coordinates : OrderedDict

    title : str

    """


# Initialization of the ``gridded_array`` class
# ----------------------------------------------------------------------------

    def __init__(self, data, coordinates, title=""):
        # TODO: Sanity-checks
        self.data = data
        # TODO: support passing coordinates as list of tuples
        self.coordinates = coordinates
        self.title = title

# Get a masked_array version of this ``gridded_data`` instance
# ----------------------------------------------------------------------------

    def masked(self):
        return gridded_array(ma.masked_invalid(self.data), self.coordinates,
                             self.title)


# Calculate mean, possible along a given axis
# ----------------------------------------------------------------------------

    def mean(self, axis=None):
        # TODO: support multiple axes at the same time, via recursion
        if axis is None:
            return bn.nanmean(self.data)
        # TODO: support specifying axes as indexed number instead of
        #       name
        if axis not in list(self.coordinates.keys()):
            raise ValueError("You asked me to calculate the mean along axis "
                             "%s, but I don't know anything about this "
                             "coordinate dimension", axis)
        # TODO: replace OrderedDict with CoordinateSet
        newcoords = OrderedDict()
        # TODO: add keys() as property to CoordinateSet
        for dim in list(self.coordinates.keys()):
            if dim != axis:
                newcoords[dim] = self.coordinates[dim]
        newdata = bn.nanmean(self.data,
                             axis=list(self.coordinates.keys()).index(axis))
        return gridded_array(newdata, newcoords, self.title)


# Return a copy of an existing ``gridded_data`` instance
# ----------------------------------------------------------------------------

    def copy(self):
        # TODO: replace OrderedDict with CoordinateSet
        newcoords = OrderedDict()
        # TODO: add keys() as property to CoordinateSet
        for dim in list(self.coordinates.keys()):
            # TODO: implement copy() method for CoordinateArray
            newcoords[dim] = self.coordinates[dim].copy()
        newdata = self.data.copy()
        return gridded_array(newdata, newcoords, self.title)


# Creating ``gridded_array`` objects
# ============================================================================

def empty(coordinates, dtype=float, masked=False):
    """Get an empty ``gridded_array`` of dtype ``dtype``."""
    if masked:
        _data = ma.empty([coordinates[dim].size for dim in list(coordinates.keys())],
                                 dtype=dtype)
    else:
        _data = np.empty([coordinates[dim].size for dim in list(coordinates.keys())],
                                 dtype=dtype)
    return gridded_array(_data, coordinates)

def ones(coordinates, dtype=float):
    """Get a ``gridded_array`` filled with ones of dtype ``dtype``."""
    return gridded_array(np.ones([coordinates[dim].size
                                         for dim in list(coordinates.keys())],
                                 dtype=dtype), coordinates)

