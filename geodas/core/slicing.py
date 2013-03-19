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

import copy

import numpy as np
import numpy.ma as ma
import pandas as pd

from geodas.core.coordinate import _array_get_common_range_index as \
                                   _get_common_range_index
from geodas import gridded_array


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
    coord_idx = [(0, coordinates[c].size) for c in list(coordinates.keys())]
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
            coord_idx[list(coordinates.keys()).index(c)] = slice_request[c]
    except ValueError:
        raise ValueError("one of the slice_request you provided for "
                         "selecting a coordinate range is not contained in "
                         "the dataset")
    coord_slices = [slice(l, u) for l, u in coord_idx]
    slices = []
    for dim, sl in zip(coordinates, coord_slices):
        if dim in list(slice_request.keys()):
            slices.append(slice(*_get_common_range_index((coordinates[dim],
                                                          (sl.start,
                                                           sl.stop)))[0]))
        else:
            slices.append(sl)
    slices = tuple(slices)
    return slices


"""We want to be able to automatically select the appropriate lambda function
with a string"""
_timeselect_funcs = {
                     "JAN" : lambda x: x.month == 1,
                     "FEB" : lambda x: x.month == 2,
                     "MAR" : lambda x: x.month == 3,
                     "APR" : lambda x: x.month == 4,
                     "MAY" : lambda x: x.month == 5,
                     "JUN" : lambda x: x.month == 6,
                     "JUL" : lambda x: x.month == 7,
                     "AUG" : lambda x: x.month == 8,
                     "SEP" : lambda x: x.month == 9,
                     "OCT" : lambda x: x.month == 10,
                     "NOV" : lambda x: x.month == 11,
                     "DEC" : lambda x: x.month == 12,
                     "MAM" : lambda x: x.month in [3, 4, 5],
                     "JJA" : lambda x: x.month in [6, 7, 8],
                     "SON" : lambda x: x.month in [9, 10, 11],
                     "DJF" : lambda x: x.month in [12, 1, 2],
                    }


def _get_timeselect_func(date, rule):
    if rule != 'monthly':
        raise ValueError()
    return lambda x: x.month == date.month and x.year == date.year


def select(gdata, **kwargs):
    """pass selection lambda function as kwargs, e.g.:

       time=lambda x: x.month == !
    """
    # TODO: this is very preliminary, and verrrry ugggly
    for kw in list(kwargs.keys()):
        if kw in list(gdata.coordinates.keys()):
            f = kwargs[kw]
            if isinstance(f, str):
                f = _timeselect_funcs[f]
            if not hasattr(f, '__call__'):
                raise ValueError("You asked me to select using a descriptor I"
                                 "don't understand!")
            if kw in ['time', 'datetime', 'date']:     # TODO
                idx = ([f(d) for d in gdata.coordinates[kw].astype(object)])
                # TODO: boolean indexing with 1d index array on 3d data
                # array doesn't work
                # uggggly workaround
                idx = np.where(idx, np.arange(len(idx), dtype=float), np.nan)
                idx = ma.masked_invalid(idx)
                idx = idx.compressed()
                idx = np.int32(idx)
                # end of ugggggly workaround
                newcoords = copy.copy(gdata.coordinates)
                newcoords['time'] = newcoords['time'][idx]
                newdata = gdata.data[idx]
                return gridded_array(newdata, newcoords, gdata.title)


def resample(gdata, **kwargs):
    """resample ``gdata`` according to rules. currently, only monthly resampling for ``time`` coordinate is supported.

       time='monthly'
    """
    # TODO: this is very preliminary, and verrrry ugggly
    # TODO: this only works if the coordinates are ordered time-long-lat
    for kw in list(kwargs.keys()):
        if kw in list(gdata.coordinates.keys()):
            if kw != 'time':
                raise ValueError("You asked me to resample along coordinate "
                                 "'%s', but I don't know how to do that." %
                                                                           kw)
            if kwargs[kw] != 'monthly':
                raise ValueError("You asked me to resample alon the time "
                                 "coordinate according to the rule '%$s', "
                                 "but I don't know now to do that." %
                                                                   kwargs[kw])
            months = pd.date_range(start=gdata.coordinates['time'].min(),
                                   end=gdata.coordinates['time'].max(),
                                   freq=pd.datetools.MonthBegin())
            data = np.ones(np.r_[months.size, gdata.data.shape[1:]]) * np.nan
            for i, m in enumerate(months):
                f = _get_timeselect_func(m, kwargs[kw])
                tmpdata = select(gdata, time=f)
                data[i] = tmpdata.mean(axis='time').data
            newcoords = copy.copy(gdata.coordinates)
            newcoords['time'] = np.datetime64(months.to_pydatetime())
            newdata = gridded_array(data, newcoords, title=gdata.title)
    return newdata


# Grouping by time
# ============================================================================

## Maybe this isn't needed after all? A simple
## ``[True if d.month == 1 else False for d in DD]`` does the trick ...
##
##def group_by_time(timesteps, **kwargs):
##    """Boolean indexing by time
##
##    Given a time span ``timesteps``, and conditions *kwargs*, return a boolean
##    array useful for boolean indexing.
##
##    Parameters
##    ----------
##    timesteps : array_like
##        Array of ``datetime.datetime`` or ``numpy.datetime64``
##
##    kwargs : int
##        The conditions on which to select the timesteps. The keys are put into
##        the conditions, so must be something like *month*, *day*, *hour*, ...
##        The values are cast to ``int``.
##
##    .. note:: Currently, only *month* and *day* are supported
##
##    Returns
##    -------
##    idx : ndarray
##
##    """
##    _selectors = {
##                  'month' : lambda x: x.month,
##                  'day' : lambda x: x.day,
##                 }
##    ts = pd.DatetimeIndex(timesteps)
##    for key in kwargs:
##        if key in _selectors.keys():
##            _selector = _selectors[key.lower()]
##            ts_map = ts.map(_selector)
##            ts = ts[ts_map == kwargs[key]]
##
##    pass

