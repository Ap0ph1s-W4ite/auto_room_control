#!/usr/bin/env python

from distutils.core import setup, Extension

setup(	name="notsmb",
	version="1.0",
	description="Python simple access to i2c-dev",
	author="Jim Spence",
	author_email="dug@byvac.com",
	maintainer="Jim Spence",
	maintainer_email="dug@byvac.com",
	license="GPLv2",
	url="http://www.byvac.com",
	ext_modules=[Extension("notsmb", ["notsmbmodule.c"])])

