# -*- coding: utf-8 -*-
#
# geodas - Geospatial Data Analysis in Python
#
# :Author:    Andreas Hilboll <andreas@hilboll.de>
# :Date:      Wed Jan 23 11:45:02 2013
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

import numpy as np

from geodas.core.coordinate import _array_get_common_range_index as \
                                   _get_common_range_index


# Prepare slice indices according to actual and requested coordinates
# ============================================================================

def get_coordinate_slices(coordinates, slice_request={}):
    """Calculate slice objects for coordinate ranges in given dimension
    variables

    Given the coordinate variables ``coordinates``, this function calculate
    the ``slice`` objects necessary to slice the region defined by
    ``slice_request`` from the coordinate arrays and the underlying dataset.
    The function returns a tuple of ``slice`` objects, which can be directly
    used in a *numpy* call to the underlying array.

    Parameters
    ----------
    coordinates : OrderedDict
        The coordinate variables of the underlying dataset

    slice_request : dict
        A dictionary ``{k : v}``, where ``k`` is the key (name) of the
        coordinate axis, as used in ``coordinates``, and ``v`` is a tuple
        ``(min, max)``. ``min`` and ``max`` must be in the same units as the
        according coordinate from ``coordinates``.

    Returns
    -------
    slices : tuple
        A tuple of ``slice`` objects.

    """
    # start with maximum slices (whole coordinate array) for each dimension
    coord_idx = [(0, coordinates[c].size) for c in coordinates.keys()]
    # overwrite for slice_request
    try:
        for c in slice_request:
            # TODO: make the list of time labels generic
            if c in ["time", "date", "datetime", ]:
                slice_request[c] = np.datetime64(slice_request[c])
            if not hasattr(slice_request[c], "__iter__"):
                # TODO: Handling the case of single requested values, i.e.
                # when slice_request[c] is a single value, is tricky and a **very**
                # bad quick fix right now.
                _add = np.timedelta64(1) if isinstance(slice_request[c],
                                                   np.datetime64) else .000001
                slice_request[c] = (slice_request[c], slice_request[c] + _add)
            coord_idx[coordinates.keys().index(c)] = slice_request[c]
    except ValueError:
        raise ValueError("one of the slice_request you provided for selecting a "
                         "coordinate range is not contained in the dataset")
    coord_slices = [slice(l, u) for l, u in coord_idx]
    slices = []
    for dim, sl in zip(coordinates, coord_slices):
        if dim in slice_request.keys():
            slices.append(slice(*_get_common_range_index((coordinates[dim],
                                                          (sl.start,
                                                           sl.stop)))[0]))
        else:
            slices.append(sl)
    slices = tuple(slices)
    return slices

