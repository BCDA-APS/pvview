#!/usr/bin/env python

# Copyright (c) 2009 - 2019, Pete Jemian.
# See LICENSE file for details.


from setuptools import setup, find_packages
import os
import re
import sys
import versioneer

# pull in some definitions from the package's __init__.py file
# sys.path.insert(0, os.path.join('src', ))
import pvview_app as package

long_description = open('README.md', 'r').read()


setup (
    name             = package.__package_name__,        # blnuhr
    license          = package.__license__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
    description      = package.__description__,
    long_description = long_description,
    author           = package.__author_name__,
    author_email     = package.__author_email__,
    url              = package.__url__,
    download_url     = package.__download_url__,
    keywords         = package.__keywords__,
    install_requires = package.__requires__,
    platforms        = 'any',
    package_dir      = {'': '.'},
    packages         = find_packages(),
    # packages         = [str(package.__package_name__), ],
    package_data     = dict(package=['LICENSE', ]),
    classifiers      = package.__classifiers__,
    entry_points={
       # create & install CLI and GUI scripts in <python>/bin
       'gui_scripts': ['pvview = pvview:main'],
       },
      )
