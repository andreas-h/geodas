# -*- coding: utf-8 -*-
"""
*****************************************************************************
geodas - Geospatial Data Analysis in Python :: Setup Script
*****************************************************************************

:Author:    Andreas Hilboll <andreas@hilboll.de>
:Date:      Sun Oct 14 12:39:25 2012

"""

from distutils.core import setup
import re

VERSIONFILE = "geodas/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='geodas',
      version=verstr,
      description='Geospatial Data Analysis in Python',
      author='Andreas Hilboll',
      author_email='andreas@hilboll.de',
      url='http://andreas-h.github.com/geodas/',
      packages=['geodas', 'geodas.core'],
      )
