# -*- coding: utf-8 -*-
#
# geodas - Geospatial Data Analysis in Python
#
# :Author:    Andreas Hilboll <andreas@hilboll.de>
# :Date:      Tue Jan 22 11:27:19 2013
# :Website:   http://andreas-h.github.com/geodas/
# :License:   GPLv3
# :Version:   0.1
# :Copyright: (c) 2012-2013 Andreas Hilboll <andreas@hilboll.de>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Library imports
# ============================================================================

from collections import OrderedDict
import datetime

import numpy as np
import pytz
import tables as tb

from geodas.core.gridded_array import gridded_array
from geodas.core.slicing import get_coordinate_slices


# Reading a ``gridded_array`` from HDF5 via *pytables*
# ============================================================================

def read_h5(filename, name=None, coords_only=False, **kwargs):
    """Read a ``gridded_array`` object from a pytables HDF5 file

    Parameters
    ----------
    filename : str
        path of the h5 file to be read

    name : str
        if more than one array is contained in the file, chose the one
            with name ``name`` in the group ``/data``.

    coords_only : bool
        if ``True``, return only the coordinate arrays; no actual data
        is read

    kwargs : tuple
        slicing of the input array can be specified using *kwargs*. The
        name of the argument must match the name of the coordinate
        variable in the opened file, and the argument's value must be a
        tuple of ``(lower_bound, upper_bound)`` of the coordinate
        variable. One or both of the bounds can be ``None``, in which
        case the bound will be set to include all data in that
        direction.

        .. note:: The bounds given as *kwargs* are **inclusive** bounds.

        .. warning::

           Passing ``None`` as upper and/or lower bound is not supported yet

    Returns
    -------
    out : gridded_array

    """
    _fd = tb.openFile(filename, "r")
    _nodes = _fd.listNodes("/data")
    # support multiple datasets per file via "name" parameter
    _dsidx = 0
    # TODO: proper exception handling
    _dsidx = 0 if name is None else [v.name for v in _nodes].index(name)
    _ds = _nodes[_dsidx]
    # read coordinates
    coord_names = _ds.attrs.COORDINATES
    coordinates = OrderedDict()
    for c in coord_names:
        coordinates[c] = _fd.getNode("/coordinates/%s" % c)[:]
        if c in ["time", "date", "datetime", ]:
            # TODO: make the list of time labels generic
            # TODO: allow for setting timzeone in variable attrs
            ts = [datetime.datetime.fromtimestamp(coordinates[c][i],
                                                  tz=pytz.utc) for
                                            i in xrange(coordinates[c].size)]
            coordinates[c] = np.datetime64(ts)
    # coordinate slicing
    slices = get_coordinate_slices(coordinates, kwargs)
    # slice the coordinate arrays themselves
    for i, c in enumerate(coord_names):
        coordinates[c] = coordinates[c][slices[i]]
    if coords_only:
        return coordinates
    # read requested slice from disk
    data = _ds[slices]
    out = gridded_array(data, coordinates, _ds.name)
    del _ds, _nodes
    _fd.close()
    return out

