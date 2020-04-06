#!/bin/bash

pip install twine
python setup.py sdist
twine upload dist/*

