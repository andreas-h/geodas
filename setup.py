# -*- coding: utf-8 -*-
"""
*****************************************************************************
geodas - Geospatial Data Analysis in Python :: Setup Script
*****************************************************************************

:Author:    Andreas Hilboll <andreas@hilboll.de>
:Date:      Sun Oct 14 12:39:25 2012

"""

NAME                = 'geodas'
MAINTAINER          = "geodas Developers"
MAINTAINER_EMAIL    = "andreas@hilboll.de"
#DESCRIPTION         = DOCLINES[0]
#LONG_DESCRIPTION    = "\n".join(DOCLINES[2:])
URL                 = "http://andreas-h.github.com/geodas"
DOWNLOAD_URL        = "http://github.com/andreas-h/geodas"
LICENSE             = 'GPL v3'
#CLASSIFIERS         = [_f for _f in CLASSIFIERS.split('\n') if _f]
AUTHOR              = "Andreas Hilboll"
AUTHOR_EMAIL        = "andreas@hilboll.de"
#PLATFORMS           = ["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"]
#MAJOR               = 1
#MINOR               = 8
#MICRO               = 0
#ISRELEASED          = False
#VERSION             = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)
    config.add_subpackage('geodas')
    config.get_version('geodas/_version.py')
    return config


if __name__ == "__main__":
    from numpy.distutils.core import setup

    setup(
          name=NAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
#          description=DESCRIPTION,
#          long_description=LONG_DESCRIPTION,
          url=URL,
          download_url=DOWNLOAD_URL,
          license=LICENSE,
#          classifiers=CLASSIFIERS,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
#          platforms=PLATFORMS,
          configuration=configuration
         )

