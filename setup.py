#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))
# with open(os.path.join(here, 'README.md')) as f:
#    description = f.read()

with open(os.path.join(dir_path, 'version'),"r") as f:
    version = f.readline().rstrip('\n')

with open(os.path.join(dir_path, 'pjname'),"r") as f:
    pjname = f.readline().rstrip('\n')

description = "A Telegram bot that allows you to receive updates from multiple social networks, sites, RSS feeds and organizations in a single feed."

install_requires = [
    'requests',
    ]

tests_require = [
    'mock>=1.0.1',
    'nose>=1.3.4',
    ]

setup(
    name=pjname,
    version=version,
    description='Telegram bot that aggregate feeds from multiple sources',
    long_description=description,
    author='Salanti Michele, Donati Ivan',
    author_email='m.salanti@campus.unimib.it, i.donati1@campus.unimib.it',
    url='https://gitlab.com/meliurwen/feedgram',
    license="GPLv3",
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
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
