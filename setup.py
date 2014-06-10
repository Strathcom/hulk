#!/usr/bin/env python

# Copyright (c) 2014 Aaron Fay / Strathcom Media http://strathcom.com/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

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
    description="Big dumb proxy server for testing service-heavy applications based on requests.",
    long_description="Acts as a proxy for service calls made with requests and caches responses for use later in tests.",
    scripts=['bin/hulk'],
    author="Aaron Fay",
    author_email="afay@strathcom.com",
    url="https://github.com/Strathcom/hulk",
    packages = ['hulk'],
    license = 'MIT',
    platforms = 'Posix; MacOS X; Windows',
    install_requires=required,
    extras_require=extras,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)