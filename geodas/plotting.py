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

from matplotlib import mpl
import matplotlib.pyplot as plt
import numpy as np


# Plotting a pcolormesh on a basemap
# ============================================================================

def pcolormesh(gdata, cbar=True, vmin=None, vmax=None, cmap=None,
               ncolors=255, proj='cyl',
               lon_0=None, lat_0=None, lat_1=None, ax=None):
    # TODO: support kwargs for basmap instance
    if len(gdata.coordinates) > 2:
        raise ValueError("You asked me to pcolormesh a dataset with dimension "
                         "%d, and I don't know how to do that.",
                         len(gdata.coordinates))
    from mpl_toolkits.basemap import Basemap
    if ax is None:
        plt.figure()
        ax = plt.gca()
    if not vmin:
        vmin = np.nanmin(gdata.data)
    if not vmax:
        vmax = np.nanmax(gdata.data)
    if not cmap:
        cmap = mpl.cm.get_cmap('jet', ncolors)
    elif isinstance(cmap, str):
        cmap = mpl.cm.get_cmap(cmap, ncolors)
    lons = gdata.coordinates['longitude']
    lats = gdata.coordinates['latitude']
    m = Basemap(llcrnrlon=lons.min(), llcrnrlat=lats.min(),
                urcrnrlon=lons.max(), urcrnrlat=lats.max(),
                projection=proj, resolution='l',
                lon_0=lon_0, lat_0=lat_0, lat_1=lat_1, ax=ax)
    m.drawcoastlines()
    m.drawmapboundary()

    if lons.ndim == 1 and lats.ndim == 1:
        LON, LAT = m(np.meshgrid(lons, lats)[0],
                     np.meshgrid(lons, lats)[1])
    elif lons.ndim == 2 and lats.ndim == 2:
        LON, LAT = m(lons, lats)

    plotdata = gdata.masked().data
    if plotdata.shape == LON.T.shape:
        plotdata = plotdata.T

    colorNorm = mpl.colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
    plot = m.pcolormesh(LON, LAT, plotdata,
                        norm=colorNorm, cmap=cmap,
                        vmin=vmin, vmax=vmax)
    if cbar:
        plt.colorbar(plot, orientation='horizontal', norm=colorNorm,
                     extend='both', spacing='uniform')
    return m

