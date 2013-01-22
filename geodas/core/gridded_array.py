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

import numpy as np

from geodas.core.coordinate import coordinate


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
        self.coordinates = coordinates
        self.title = title


# Reading a ``gridded_array`` from HDF5 via *pytables*
# ============================================================================

def read_h5(filename):
    pass
