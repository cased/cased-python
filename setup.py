import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


setup(
    name="pycased",
    version="0.4.0",
    description="Python library for Cased",
    long_description="Python library for Cased",
    author="Cased",
    author_email="support@cased.com",
    url="https://github.com/cased/cased-python",
    license="MIT",
    keywords="cased api",
    packages=find_packages(exclude=["tests", "tests.*"]),
    zip_safe=False,
    python_requires=">3.5",
    install_requires=[
        "requests",
        "responses",
        "mock",
        "pytest >= 4.00",
        "pytest-mock",
        "pytest-xdist",
        "freezegun",
        "redis",
        "deepmerge",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/cased/cased-python/issues",
        "Documentation": "https://docs.cased.com/api",
        "Source Code": "https://github.com/cased/cased-python",
    },
)
