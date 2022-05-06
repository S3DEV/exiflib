#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:App:       setup.py
:Purpose:   Python library packager.

:Version:   0.2.0
:Platform:  Linux/Windows | Python 3.8
:Developer: J Berendt
:Email:     development@s3dev.uk

:Example:
    Create source and wheel distributions::

        cd /path/to/package
        python setup.py sdist bdist_wheel

    Simple installation::

        cd /path/to/package/dist
        pip install <pkgname>-<...>.whl --no-deps

    git installation::

        pip install git+file:///<drive>:/path/to/package --no-deps

    github installation::

        pip install git+https://github.com/s3dev/<pkgname>

"""
# pylint: disable=too-few-public-methods

import os
from setuptools import setup, find_packages
from exiflib._version import __version__


class Setup:
    """Create a dist package for this library."""

    PACKAGE         = 'exiflib'
    VERSION         = __version__
    PLATFORMS       = 'Python 3.6+'
    MIN_PYTHON      = '>=3.6'
    DESC            = ('Extract exif data from an image and return as a '
                       'Pandas Series.')
    AUTHOR          = 'J. Berendt'
    AUTHOR_EMAIL    = 'support@s3dev.uk'
    URL             = 'https://github.com/s3dev/exiflib'
    LICENSE         = 'MIT'
    ROOT            = os.path.realpath(os.path.dirname(__file__))
    PACKAGE_ROOT    = os.path.join(ROOT, PACKAGE)
    INCL_PKG_DATA   = False
    CLASSIFIERS     = ['Development Status :: 5 - Production/Stable'
                       'Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Programming Language :: Python :: 3.8',
                       'Programming Language :: Python :: 3.9',
                       'Programming Language :: Python :: 3.10',
                       'License :: OSI Approved :: MIT License',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX :: Linux',
                       'Topic :: Software Development',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities']

    # PACKAGE REQUIREMENTS
    REQUIRES        = ['Pillow>=9.0', 'utils4', 'pandas']
    PACKAGES        = find_packages()

    # ADD DATA AND DOCUMENTATION FILES
    DATA_FILES      = []
    PACKAGE_DATA    = {'exiflib': ['LICENSE']}

    def run(self):
        """Run the setup."""
        setup(name=self.PACKAGE,
              version=self.VERSION,
              platforms=self.PLATFORMS,
              python_requires=self.MIN_PYTHON,
              description=self.DESC,
              author=self.AUTHOR,
              author_email=self.AUTHOR_EMAIL,
              maintainer=self.AUTHOR,
              maintainer_email=self.AUTHOR_EMAIL,
              url=self.URL,
              license=self.LICENSE,
              packages=self.PACKAGES,
              install_requires=self.REQUIRES,
              data_files=self.DATA_FILES,
              include_package_data=self.INCL_PKG_DATA,
              classifiers=self.CLASSIFIERS,
              package_data=self.PACKAGE_DATA)

if __name__ == '__main__':
    Setup().run()
