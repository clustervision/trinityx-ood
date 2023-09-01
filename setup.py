#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup file, will build the pip package for the project.
"""

__author__      = 'Sumit Sharma'
__copyright__   = 'Copyright 2022, Trinity[OOD]'
__license__     = 'GPL'
__version__     = '2.0'
__maintainer__  = 'Sumit Sharma'
__email__       = 'sumit.sharma@clustervision.com'
__status__      = 'Development'

from time import time
import pathlib
from setuptools import setup, find_packages

PRE = "{Personal-Access-Token-Name}:{Personal-Access-Token}"
DIR = pathlib.Path(__file__).parent.resolve()

try: # for pip >= 10
    from pip._internal.req import parse_requirements
    install_requirements = list(parse_requirements(f'{DIR}/requirements.txt', session='hack'))
    requirements = [str(ir.requirement) for ir in install_requirements]
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    install_requirements = parse_requirements('requirements.txt', session='hack')
    requirements = [str(ir.req) for ir in install_requirements]


def new_version():
    """
    This Method will create a New version and update the Version file.
    """
    time_now = int(time())
    version = f'2.0.{time_now}'
    with open(f'{DIR}/VERSION.txt', 'w', encoding='utf-8') as ver:
        ver.write(version)
    return version


setup(
	name = "trinity-ood",
	version = new_version(),
	description = "Trinity Open On Demand Application to support GUI via Luna 2 Daemon.",
	long_description = "This project will serve the GUI via Luna2 Daemon.\
        This project is a part of Trinity Open On Demand.",
	author = "Sumit Sharma",
	author_email = "sumit.sharma@clustervision.com",
	maintainer = "Sumit Sharma",
	maintainer_email = "sumit.sharma@clustervision.com",
	url = "https://gitlab.taurusgroup.one/clustervision/trinity-ood.git",
	download_url = f"https://{PRE}@gitlab.taurusgroup.one/api/v4/projects/30/packages/pypi/simple",
	packages = find_packages(),
	license = "MIT",
	keywords = ["luna", "ood", "GUI", "Trinity", "ClusterVision", "Sumit", "Sumit Sharma"],
	entry_points = {
		'console_scripts': [
			'trinity = bmcsetup.app:main'
		]
	},
	install_requires = requirements,
	dependency_links = [],
	data_files = [],
	zip_safe = False,
	include_package_data = True,
	classifiers = [
		'Development Status :: Beta',
		'Environment :: Web Interface',
		'Intended Audience :: System Administrators',
		'License :: MIT',
		'Operating System :: RockyLinux :: CentOS :: RedHat',
		'Programming Language :: Python',
		'Topic :: Trinity :: Luna'
	],
	platforms = [
		'RockyLinux',
		'CentOS',
		'RedHat'
	]
)
# python setup.py sdist bdist_wheel
