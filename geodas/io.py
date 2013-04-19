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
import getpass
import os.path
import pdb
import socket
import sys
import time

import numpy as np
import pandas as pd

import geodas
from geodas.core.gridded_array import gridded_array
from geodas.core.slicing import get_coordinate_slices


# Auxiliary tools and functions
# ============================================================================

# sometimes it's necessary to guess if a variable name belongs to a
# coordinate variable or to a data variable
_possible_coordinate_names = ['lat', 'lats', 'latitude', 'latitudes', 'y',
                              'lon', 'lons', 'longitude', 'longitudes', 'x',
                              'time', 'date', 'datetime']

def _is_name_coordinate(name):
    return name.lower() in _possible_coordinate_names

_datetime_coordinates = ['time', 'date', 'datetime', ]

def _is_datetime_coordinate(name):
    return name.lower() in _datetime_coordinates

def _guess_units(name):
    if _is_datetime_coordinate(name):
        return "hours since 1994-01-01 00:00:00 +0:00"
    elif name.lower() in ['lat', 'lats', 'latitude', 'latitudes', 'y', ]:
        return "degrees_north"
    elif name.lower() in ['lon', 'lons', 'long', 'longs', 'longitude',
                          'longitudes', 'x', ]:
        return "degrees_east"
    raise ValueError("You passed the name {0}, but I don't know which units "
                     "this coordinate might be in".format(name))


# netCDF, via python-netcdf4
# ============================================================================

def _guess_netcdf_dimensions(_file):
    """get an ``OrderedDict`` of all 1d-variables within ``_file``, with the
    dimension's name/descriptor as key and a tuple (variable-name,
    variable-stdname) as value"""
    dimvars = OrderedDict()
    for var in list(_file.variables.keys()):
        if len(_file.variables[var].dimensions) == 1:
            dimname = _file.variables[var].dimensions[0]
            if dimname in list(dimvars.keys()):
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

    .. todo:: Implement climatologies according to CF-conventions

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
                        set([n for (n, s) in list(dimensions.values())])))
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
            tmpdates = netCDF4.num2date(
                                      coordinates[coord_names[var]],
                                      _file.variables[var].getncattr('units'),
                                      _calendar)
            tmpdates = np.array([np.datetime64(tmpdates[i]) for i in range(tmpdates.size)])
            coordinates[coord_names[var]] = tmpdates
    # coordinate slicing
    slices = get_coordinate_slices(coordinates, kwargs)
    # slice the coordinate arrays themselves
    for i, c in enumerate(list(coordinates.keys())):
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
        Full path to the data node in the HDF5 file. If *name* does not start
        with a *slash* ``/``, ``read_hdf5`` will attempt to read the node with
        name *name* in the group ``/data``. If ``None``, ``read_hdf5`` will
        attempt to find exactly one array in the group ``/data`` and read
        this; otherwise, an exception is raised.

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

    Note
    ----
    ``read_hdf5`` expects to find the names of the coordinate dimensions in a
    data attribute named ``COORDINATES``. It will first search for nodes with
    these names in the current group, and if no coordinate dimension arrays
    are contained in that group, it will try to read the coordinate dimensions
    from the group ``/coordinates``.

    """
    import pytz
    import tables as tb
    _fd = tb.openFile(filename, "r")
    if str(name).startswith('/'):
        try:
            _ds = _fd.getNode(str(name))
        except:
            raise ValueError("I cannot read the dataset at node %s" % name)
    else:
        try:
            _nodes = _fd.listNodes("/data")
        except:
            raise ValueError("You didn't specify a full path to the dataset "
                             "you want me to read, but there is no group "
                             "/data in the file.")
        if name is None and len(_nodes) != 1:
            raise ValueError("You didn't provide a dataset name, and this "
                             "file contains more or less than exactly one "
                             "dataset in the group /data.")
        # support multiple datasets per file via "name" parameter
        _dsidx = 0
        # TODO: proper exception handling
        try:
            _dsidx = (0 if name is None
                        else [v.name for v in _nodes].index(name))
        except:
            raise ValueError("You asked me to read dataset %s from group "
                             "/data, but this dataset doesn't exist")
        _ds = _nodes[_dsidx]
    # read coordinates
    _dsgroup = _ds._v_parent._v_pathname
    coord_names = _ds.attrs.COORDINATES
    def _read_coords_from_group(grp, coord_names):
        coordinates = OrderedDict()
        for c in coord_names:
            coordinates[c] = _fd.getNode("%s/%s" % (grp, c))[:]
            if c in ["time", "date", "datetime", ]:
                # TODO: make the list of time labels generic
                # TODO: allow for setting timzeone in variable attrs
                ts = [datetime.datetime.fromtimestamp(coordinates[c][i],
                                                      tz=pytz.utc) for
                                             i in range(coordinates[c].size)]
                coordinates[c] = np.datetime64(ts)
        return coordinates
    try:
        coordinates = _read_coords_from_group(_dsgroup, coord_names)
    except:
        try:
            coordinates = _read_coords_from_group("/coordinates", coord_names)
        except:
            raise AttributeError("I cannot find any coordinate variable data "
                                 "for the requeted data object")
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
    del _ds
    try:
        del _nodes
    except:
        pass
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
    for i, c in enumerate(list(coordinates.keys())):
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

def read_hdf4(filename, name=None, coords_only=False, **kwargs):
    import pyhdf.SD as SD
    from pyhdf.error import HDF4Error
    try:
        _file = SD.SD(filename)
    except HDF4Error:
        print("Cannot open file: %s" % filename)
        raise
    # find out which dataset to read
    if name is None:
        datasets = list(_file.datasets().keys())
        variables = []
        for d in datasets:
            var = _file.select(d)
            if len(var.dimensions()) > 1 or var.dim(0).info()[0] != d:
                variables.append(d)
        if len(variables) > 1:
            raise AttributeError("There is more than one non-coordinate "
                                 "variable in the file, and you didn't "
                                 "specify which one you want me to read!")
        name = variables[0]
    # open dataset
    sds = _file.select(name)
    # open the coordinate variables
    dims = sds.dimensions(full=True)
    dimorder = {dims[k][1] : k for k in list(dims.keys())}
    coordinates = OrderedDict()
    for d in range(len(dimorder)):
        coordinates[dimorder[d]] = _file.select(dimorder[d])[:]
    # coordinate slicing
    slices = get_coordinate_slices(coordinates, kwargs)
    # slice the coordinate arrays themselves
    for i, c in enumerate(list(coordinates.keys())):
        coordinates[c] = coordinates[c][slices[i]]
    if coords_only:
        return coordinates
    # read requested slice from disk
    data = sds[slices]
    fill = sds.getfillvalue()
    if fill is not None and not np.isnan(fill):
        data = np.where(data != fill, data, np.nan)
    out = gridded_array(data, coordinates, name)
    _file.end()
    return out


# Write a ``gridded_array`` object to netCD, via python-netcdf4
# ============================================================================

def write_netcdf(data, filename, metadata={}, fillvalue=np.nan,
                 varname="DATA", varunits="UNDEF",
                 overwrite=False, format="NETCDF4_CLASSIC", complib=None,
                 complevel=4, shuffle=True, fletcher32=False,
                 contiguous=False, chunksizes=None, endian='native',
                 least_significant_digit=None):
    """Write a ``gridded_array`` object to a netCDF file

    Parameters
    ----------
    data : gridded_array
        the data object to write to file

    filename : str
        path of the netCDF file to be read

    metadata : dict
        a dictionary of additional metadata attributes to be added to the
        file.

    fillvalue : float

    varname : str

    overwrite : bool
        If *True*, overwrite potentially existing files. If *False*, raise an
        exception.

    format : str
        Underlying file format (one of ``NETCDF4``, ``NETCDF4_CLASSIC``,
        ``NETCDF3_CLASSIC``, or ``NETCDF3_64BIT``. Defaults to ``NETCDF4``,
        which means the data is stored in an HDF5 file, using netCDF 4 API
        features. Setting format=``NETCDF4_CLASSIC`` will create an HDF5 file,
        using only netCDF 3 compatibile API features.  netCDF 3 clients must
        be recompiled and linked against the netCDF 4 library to read files in
        NETCDF4_CLASSIC format. ``NETCDF3_CLASSIC`` is the classic netCDF 3
        file format that does not handle 2+ Gb files very well.
        ``NETCDF3_64BIT`` is the 64-bit offset version of the netCDF 3 file
        format, which fully supports 2+ GB files, but is only compatible with
        clients linked against netCDF version 3.6.0 or later.

    complib : str
        Can be either *zlib* or *None*. If set to *zlib*, the data will be
        compressed in the netCDF file using gzip compression.

    complevel : int
        An integer between 1 and 9 describing the level of compression
        desired. Ignored if *complevel=None*.

    shuffle : bool
        If *True*, the HDF5 shuffle filter will be applied before compressing
        the data. This significantly improves compression. Ignored if
        *complib=None*.

    fletcher32 : bool
        If *True*, the Fletcher32 HDF5 checksum algorithm is activated to
        detect errors.

    contiguous : bool
        If *True*, the variable data is stored contiguously on disk. Setting
        to *True* for a variable with an unlimited dimension will trigger an
        error.

    chunksizes=None
        Manually specify the HDF5 chunksizes for each dimension of the
        variable. A detailed discussion of HDF chunking and I/O performance is
        available `here
        <http://www.hdfgroup.org/HDF5/doc/H5.user/Chunking.html>`__.
        Basically, you want the chunk size for each dimension to match as
        closely as possible the size of the data block that users will read
        from the file. *chunksizes* cannot be set if *contiguous=True*.

    endian : str
         Possible values are *little*, *big*, or *native*. The netCDF4 library
         will automatically handle endian conversions when the data is read,
         but if the data is always going to be read on a computer with the
         opposite format as the one used to create the file, there may be some
         performance advantage to be gained by setting the endian-ness.

    least_significant_digit=None
        If specified, variable data will be truncated (quantized). In
        conjunction with *complib=zlib*, this produces 'lossy', but
        significantly more efficient compression. For example, if
        *least_significant_digit=1*, data will be quantized using
        numpy.around(scale*data)/scale, where scale = 2**bits, and bits is
        determined so that a precision of 0.1 is retained (in this case
        bits=4). From
        http://www.cdc.noaa.gov/cdc/conventions/cdc_netcdf_standard.shtml:
        "least_significant_digit -- power of ten of the smallest decimal place
        in unpacked data that is a reliable value." *None* means no
        quantization, or 'lossless' compression.

    .. todo:: Add possibility to add a new array to an existing file, making
              sure that the dimensions match.

    .. todo:: Implement climatologies according to CF-conventions

    .. todo:: Read *varname* and *varunits* from input data object

    """
    import netCDF4
    if not overwrite and os.path.isfile(filename):
        raise IOError("Output file {f} already exists!".format(f=filename))

    # create the netCDF file
    try:
        _f = netCDF4.Dataset(filename, 'w', clobber=overwrite, format=format)
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        print("I/O error({0}): {1}".format(errno, strerror))
        raise
    except:
        print("Unexpected error creating NC file:", sys.exc_info()[0])
        raise

    # Create dimension variables
    dims = OrderedDict()
    for key, dim in list(data.coordinates.items()):
        assert dim.ndim == 1
        _f.createDimension(key, dim.size)
        _dtype = dim.dtype if not _is_datetime_coordinate(key) else "f8"
        _v = _f.createVariable(key, _dtype, (key, ))
        _v.standard_name = key
        try:
            _v.units = dim.units
        except AttributeError:
            _v.units = _guess_units(key)
        if not _is_datetime_coordinate(key):
            _v[:] = dim[:]
        else:
            _v.calendar = "gregorian"
            _v[:] = netCDF4.date2num(pd.to_datetime(dim).to_pydatetime(),
                                     _v.units, _v.calendar)
        dims[key] = _v


    # Create data variable
    datavar = _f.createVariable(varname, data.data.dtype, list(dims.keys()),
                                zlib=(True if complib == "zlib" else False),
                                complevel=complevel, fletcher32=fletcher32,
                              least_significant_digit=least_significant_digit)
    datavar.standard_name = varname
    datavar.units = varunits
    datavar[:] = data.data

    # Add metadata
    _f.Conventions = "CF-1.6"
    _f.history     = "Created on {0} by {1}@{2} using geodas v{3}".format(
                         time.ctime(), getpass.getuser(), socket.getfqdn(),
                         geodas.__version__)

    # Add custom metadata
    _attrs = _f.ncattrs()
    for key, item in list(metadata.items()):
        if key not in _attrs:
            _f.setncattr(key, item)

    # cleanup
    _f.close()
    del _f
