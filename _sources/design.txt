.. include:: shorthand.rst

******************************************************************************
Design goals
******************************************************************************

In many geosciences, like in atmospheric science, a repeating task is the
handling and analysis of large four-dimensional datasets, i.e. timeseries of
3d atmospheric data (with the dimensions altitude, longitude, and latitude).
The pandas_ library is an excellent tool for the analysis of such large
datasets; however, the terminology it uses (e.g. *index*, *column*,
*major_axis*, *minor_axis*) is awkward for many from the field of geoscience.

The goal of |geodas| is to build upon pandas while making the every-day work
of a geoscientist as comfortable as possible. The library allows access to 
the data's dimensions via their names (*altitude*, *longitude*, *latitude*,
*time*), facilitates easy plotting (via matplotlib_ and its basemap_
toolkit), and allows direct file i/o of common geoscience data formats
(via HDF4_, netCDF4_, and GDAL_).


Basic data object
==============================================================================

A basic data object in |geodas| can be 2-, 3-, or 4-dimensional. Each
dimension is realized similar to the ``Index`` class in pandas_. A dimension
gets a *name*, a *value* array and a *unit*. Cyclic variables (like longitude,
or climatologies) will be supported. When performing basic arithmetic with
data objects, automatic care will be taken that the dimensions actually agree:
|geodas| will automatically transpose data to align properly for the
operation, or will raise a warning in case the dimensions do not match. Data
objects will automatically be broadcast to match each other if the other
dimensions agree. Access to the data's dimensions can be done using the
dimension's *name*; there will be no need to remember the data's dimensions'
order. Masked values will be automatically supported.


Regridding data
==============================================================================

|geodas| will support several interpolation and averaging methods to regrid
data objects to a finer and coarser grid, respectively.


Plotting routines
==============================================================================

|geodas| will build on matplotlib_ to support a wide range of plotting
routines in an intuitive way.

