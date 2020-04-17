#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# with open(os.path.join(here, 'README.md')) as f:
#    description = f.read()

with open(os.path.join(DIR_PATH, 'version'), "r") as f:
    VERSION = f.readline().rstrip('\n')

with open(os.path.join(DIR_PATH, 'pjname'), "r") as f:
    PJNAME = f.readline().rstrip('\n')

DESCRIPTION = "A Telegram bot that allows you to receive updates from multiple social networks, sites, RSS feeds and organizations in a single feed."

INSTALL_REQUIRES = [line.rstrip('\n') for line in open('requirements.txt')]

TESTS_REQUIRE = [line.rstrip('\n') for line in open('test-requirements.txt')]

setup(
    name=PJNAME,
    version=VERSION,
    description='Telegram bot that aggregate feeds from multiple sources',
    long_description=DESCRIPTION,
    author='Salanti Michele, Donati Ivan',
    author_email='m.salanti@campus.unimib.it, i.donati1@campus.unimib.it',
    url='https://gitlab.com/meliurwen/feedgram',
    license="GPLv3",
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    test_suite="pytest",
    include_package_data=True,
    keywords=['telegram', 'bot', 'feed', 'feeds', 'instagram'],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': ['app = app.app_handler:main']
    },
)
