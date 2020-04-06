#!/bin/sh

sphinx-apidoc --ext-githubpages --ext-autodoc --ext-todo --ext-coverage -f -o _modules ../rxn4chemistry
