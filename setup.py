#!/usr/bin/env python

import io
import os
import re

from setuptools import setup, find_packages

version_match = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open("rxn4chemistry/__init__.py", encoding="utf_8_sig").read(),
)
if version_match is None:
    raise ValueError("Version could not be determined")
__version__ = version_match.group(1)

if os.path.exists("README.md"):
    long_description = open("README.md").read()
else:
    long_description = """Python wrapper for the IBM RXN for Chemistry API"""

setup(
    name="RXN4Chemistry",
    version=__version__,
    author="RXN for Chemistry team",
    author_email=(
        "phs@zurich.ibm.com, tte@zurich.ibm.com, obc@zurich.ibm.com, "
        "ava@zurich.ibm.com, dpr@zurich.ibm.com"
    ),
    py_modules=["RXN4Chemistry"],
    description="Python wrapper for IBM RXN for Chemistry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires=["requests==2.23.0", "beautifulsoup4==4.9.0"],
    packages=find_packages(),
    url="https://github.com/rxn4chemistry/rxn4chemistry",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
