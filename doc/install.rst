.. include:: shorthand.rst

******************************************************************************
Installation
******************************************************************************

Prerequisites
==============================================================================

|geodas| heavily depends on the pandas_ library. Currently, the minimum
version of pandas supported is ``0.9.0``.
For efficient interactive use of |geodas|, we strongly suggest using ipython_
at version at least ``0.13``.


Download
==============================================================================

At the moment, the only way to install |geodas| is to check out the source at
`github <http://github.com/andreas-h/geodas/>`_:

.. code-block:: bash

   user@workstation:~$ git clone https://github.com/andreas-h/geodas.git

Source tarballs to download will be provided in the future.


Installation using *distutils*
==============================================================================

Currently, |geodas| builds on distutils_ to support an easy way of
installation. Ideally, the installation of |geodas| is a simple

.. code-block:: bash

   user@workstation:~$ python setup.py install

