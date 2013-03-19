# -*- coding: utf-8 -*-
"""
*****************************************************************************
geodas - Geospatial Data Analysis in Python
*****************************************************************************

:Author:    Andreas Hilboll <andreas@hilboll.de>
:Date:      Sat Oct 13 21:40:15 2012
:Website:   http://andreas-h.github.com/geodas/
:License:   GPLv3
:Version:   0.1
:Copyright: (c) 2012 Andreas Hilboll <andreas@hilboll.de>

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

from _version import __version__

__version_info__ = tuple([ int(num) for num in __version__.split('.')])

__docformat__ = 'restructuredtext'

import pkg_resources

# Python 2.7 is needed because the ``dimension`` is implemented as an
# ``OrderedDict``.
pkg_resources.require("python>=2.7")

pkg_resources.require("bottleneck>=0.6.0")
pkg_resources.require("pandas>=0.9.0")


from core.gridded_array import gridded_array, ones
from core.slicing import resample, select

from io import read_gdal, read_hdf4, read_hdf5, read_netcdf4
from io import write_netcdf


# load site configuration
from ConfigParser import ConfigParser
import os.path
_C = ConfigParser()
_C.read(os.path.join(os.environ['HOME'], '.geodasrc'))

__config__ = {}
try:
    for _k, _v in _C.items('geodas'):
        __config__[_k] = _v
    del _C, _k, _v
except:
    pass
