#!/usr/bin/env python
# coding: utf-8
from setuptools import find_packages, setup

from rlapi.constants import VERSION

setup(
    name="python-rocket-league",
    version=".".join(str(n) for n in VERSION),
    url="https://github.com/rocket-league-replays/python-rocket-league",
    author="Daniel Samuels",
    author_email="daniel@rocketleaguereplays.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='Client library for the official Rocket League API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['requests'],
    extras_require={
        'testing': [
            'coverage',
            'pytest',
            'pytest-cov',
            'pytest-xdist',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)
