# -*- coding: utf-8 -*-
"""
*****************************************************************************
geodas - Geospatial Data Analysis in Python
*****************************************************************************

:Author:    Andreas Hilboll <andreas@hilboll.de>
:Date:      Mon Jan 21 19:52:07 2013
:Website:   http://andreas-h.github.com/geodas/
:License:   GPLv3
:Version:   0.1
:Copyright: (c) 2012-2013 Andreas Hilboll <andreas@hilboll.de>

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

# Library imports
# ============================================================================

import numpy as np

from geodas.core.dimension import _array_get_common_range_index


def _test_array_get_common_range_index():
    d1 = np.arange(12) + .5
    d2 = np.arange(3, 8)
    d3 = np.arange(4, 16)
    bounds = _array_get_common_range_index((d1, d2, d3))
    assert bounds[0] == (4, 7)
    assert bounds[1] == (1, 5)
    assert bounds[2] == (0, 4)
    print("success")

if __name__ == "__main__":
    _test_array_get_common_range_index()
