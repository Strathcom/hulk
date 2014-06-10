#!/usr/bin/env python
from setuptools import setup

from hulk import __title__ as title
from hulk import __version__ as version

required = [
    'Flask',
    'requests',
    'docopt',
]

extras = {
    'develop': [
        'nose',
        'coverage',
    ]
}

setup(
    name=title,
    version=version,
    description="Big dumb proxy server for testing service-heavy applications.",
    scripts=['bin/hulk'],
    author="Aaron Fay",
    author_email="afay@strathcom.com",
    packages = ['hulk'],
    install_requires=required,
    extras_require=extras,
)