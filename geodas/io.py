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
import pdb

import numpy as np

from geodas.core.gridded_array import gridded_array
from geodas.core.slicing import get_coordinate_slices


# Auxiliary tools and functions
# ============================================================================

# sometimes it's necessary to guess if a variable name belongs to a
# coordinate variable or to a data variable
_possible_coordinate_names = ['lat', 'lats', 'latitude', 'latitudes', 'y',
                              'lon', 'lons', 'longitude', 'longitudes', 'x',
                              'time', 'date', 'datetime']

def is_name_coordinate(name):
    return name.lower() in _possible_coordinate_names


# netCDF, via python-netcdf4
# ============================================================================

def _guess_netcdf_dimensions(_file):
    """get an ``OrderedDict`` of all 1d-variables within ``_file``, with the
    dimension's name/descriptor as key and a tuple (variable-name,
    variable-stdname) as value"""
    dimvars = OrderedDict()
    for var in _file.variables.keys():
        if len(_file.variables[var].dimensions) == 1:
            dimname = _file.variables[var].dimensions[0]
            if dimname in dimvars.keys():
                raise ValueError("There are more than one 1D-variables %s "
                                 "sharing the same dimension %s in this "
                                 "file. I cannot unambigously continue like "
                                 "that." % (dimvars[dimname], var, dimname))
            if 'standard_name' in _file.variables[var].ncattrs():
                stdname = _file.variables[var].standard_name
            elif var.lower() in ['y', 'lat', 'latitude', ]:
                stdname = 'latitude'
            elif var.lower() in ['x', 'lon', 'longitude', ]:
                stdname = 'longitude'
            dimvars[dimname] = (var, stdname)

    return dimvars


def read_netcdf4(filename, name=None, coords_only=False, **kwargs):
    """Read a ``gridded_array`` object from a netCDF file

    Parameters
    ----------
    filename : str
        path of the netCDF file to be read

    name : str
        if more than one array is contained in the file, chose the one
            with name ``name``.

    coords_only : bool
        if ``True``, return only the coordinate arrays; no actual data
        is read

    kwargs : tuple
        slicing of the input array can be specified using *kwargs*. The name
        of the argument must match the name of the coordinate variable in the
        opened file, and the argument's value must be a tuple of
        ``(lower_bound, upper_bound)`` of the coordinate variable. One or both
        of the bounds can be ``None``, in which case the bound will be set to
        include all data in that direction.

        .. note:: The bounds given as *kwargs* are **inclusive** bounds.

        .. warning::

           Passing ``None`` as upper and/or lower bound is not supported yet

    Returns
    -------
    out : gridded_array

    Notes
    -----
    This function can only read files where no two 1-dimensional variables
    share the same dimension.

    """
    import netCDF4
    try:
        _file = netCDF4.Dataset(filename, 'r')
    except:
        raise IOError("Cannot open netCDF4 file %s" % filename)
    # entangle dimension / variable mess
    dimensions = _guess_netcdf_dimensions(_file)
    # Which data variables are in the file?
    if name is None:
        # list subtraction. datavars is all variable labels which are
        # not label of a dimension variable
        datavars = list(set(_file.variables.keys()).difference(
                        set([n for (n, s) in dimensions.values()])))
        # additionally, we remove some typical variable names which arise from
        # netcdf conventions
        for varname in ['climatology_bounds', 'crs', ]:
            if varname in datavars:
                datavars.pop(datavars.index(varname))
        if len(datavars) > 1:
            raise AttributeError("There is more than one non-coordinate "
                                 "variable in the file, and you didn't "
                                 "specify which one you want me to read!")
        name = datavars[0]
    datavar = _file.variables[name]
    # Read coordinates
    coord_shortnames = datavar.dimensions   # the name of the nc-dimension
    coord_stdnames = [dimensions[dim][1] for dim in coord_shortnames]
    #coord_stdnames = [s for (n, s) in dimensions.values()]   # nc-std-names
    coord_names = {k : str(v) for (k, v) in zip(coord_shortnames,  # our names
                                                coord_stdnames)}
    coordinates = OrderedDict()
    for var in coord_shortnames:
        coordinates[coord_names[var]] = _file.variables[dimensions[var][0]][:]
        if coord_names[var] in ['time', 'date', 'datetime']:   # TODO
            _calendar = (_file.variables[var].getncattr('calendar')
                               if 'calendar' in _file.variables[var].ncattrs()
                               else 'standard')
            coordinates[coord_names[var]] = netCDF4.num2date(
                                      coordinates[coord_names[var]],
                                      _file.variables[var].getncattr('units'),
                                      _calendar)
            coordinates[coord_names[var]] = np.datetime64(
                                                coordinates[coord_names[var]])
    # coordinate slicing
    slices = get_coordinate_slices(coordinates, kwargs)
    # slice the coordinate arrays themselves
    for i, c in enumerate(coordinates.keys()):
        coordinates[c] = coordinates[c][slices[i]]
    if coords_only:
        return coordinates
    # read requested slice from disk
    data = datavar[slices]
    # mask array
    try:
        _fill = datavar.getncattr('_FillValue')
    except:
        _fill = None
    if _fill is not None and not np.isnan(_fill):
        data = np.where(data != _fill, data, np.nan)
    dataname = (datavar.standard_name if 'standard_name'
                                      in datavar.ncattrs()
                                      else name)
    out = gridded_array(data, coordinates, dataname)
    _file.close()
    del data
    return out


# HDF5, via pytables
# ============================================================================

def read_hdf5(filename, name=None, coords_only=False, **kwargs):
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
    import pytz
    import tables as tb
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


# GDAL
# ============================================================================

def read_gdal(filename, band=1, coords_only=False, **kwargs):
    """Read a ``gridded_array`` object via the GDAL library

    Parameters
    ----------
    filename : str
        path of the h5 file to be read

    band : int
        if more than one array is contained in the file, chose the one
        with the RasterBand id ``band`` (starting at 1).

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

    Notes
    -----

    .. todo:: **TODO**

       read ``AREA_OR_POINT`` from raster band definition

    """
    from osgeo import gdal
    from osgeo.gdalconst import GA_ReadOnly
    _file = gdal.Open(filename, GA_ReadOnly)
    # read coordinates
    _geo = _file.GetGeoTransform()
    minlon, lonstep, tmp0, maxlat, tmp1, latstep = _geo
    nlon = _file.RasterXSize
    nlat = _file.RasterYSize
    coordinates = OrderedDict()
    coordinates['longitude'] = np.linspace(minlon + .5 * lonstep,
                                           minlon + (nlon - .5) * lonstep,
                                           nlon)
    coordinates['latitude'] = np.linspace(maxlat + .5 * latstep,
                                          maxlat + (nlat - .5) * latstep,
                                          nlat)
    # coordinate slicing
    slices = get_coordinate_slices(coordinates, kwargs)
    # slice the coordinate arrays themselves
    for i, c in enumerate(coordinates.keys()):
        coordinates[c] = coordinates[c][slices[i]]
    if coords_only:
        return coordinates
    # find out which rasterband to read
    band = _file.GetRasterBand(band)
    data = band.ReadAsArray()
    fill = band.GetNoDataValue()
    if fill is not None and not np.isnan(fill):
        data = np.where(data != fill, data, np.nan)
    # TODO: check if data and lats need to be reordered
    #if np.diff(lats).max() < 0.:
    #    lats = lats[::-1]
    #    data = data[::-1]
    # read requested slice from disk
    data = data[slices]
    out = gridded_array(data, coordinates, "")
    return out


# HDF4 Scientific Dataset
# ============================================================================

#def read_hdf4(filename, param=None):
#    import pyhdf.SD as SD
#    try:
#        _file = SD.SD(filename)
#    except Exception:
#        print "Cannot open file: %s" % filename
#        raise
#    _params = _file.datasets().keys()
#    while param == None:
#        for p in _params:
#            if p not in ['latitude', 'longitude']:
#                param = p
#    sds = _file.select(param)[:].copy()
#    lats = _file.select("latitude")[:].copy()
#    lons = _file.select("longitude")[:].copy()
#    _tmpdata = sds[:]
#    _file.end()
#    if np.isnan(_tmpdata).any():
#        data = ma.masked_invalid(_tmpdata)
#    else:
#        data = _tmpdata
#    if np.diff(lats).max() < 0.:
#        lats = lats[::-1]
#        data = data[::-1]
#    retval = GriddedData(data, lats, lons)
#    del _file, data, _tmpdata, lats, lons
#    return retval
