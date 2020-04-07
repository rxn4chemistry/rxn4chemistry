# Python wrapper for the IBM RXN for Chemistry API

[![Build Status](https://travis-ci.org/rxn4chemistry/rxn4chemistry.svg?branch=master)](https://travis-ci.org/rxn4chemistry/rxn4chemistry)
[![PyPI version](https://badge.fury.io/py/RXN4Chemistry.svg)](https://badge.fury.io/py/RXN4Chemistry)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![logo](./docs_source/_static/logo.jpg)

A python wrapper to access the API of the IBM RXN for Chemistry [website](https://rxn.res.ibm.com/rxn/).

## Install

From PYPI:

```console
pip install rxn4chemistry
```

Or directly from the repo:

```console
pip install git+https://github.com/rxn4chemistry/rxn4chemistry.git
```

## Usage

### Create a project

Get your API key from [here](https://rxn.res.ibm.com/rxn/user/profile) and build the wrapper:

```python
api_key='API_KEY'
from rxn4chemistry import RXN4ChemistryWrapper

rxn4chemistry_wrapper = RXN4ChemistryWrapper(api_key=api_key)
# NOTE: you can create a project or set an esiting one using:
# rxn4chemistry_wrapper.set_project('PROJECT_ID')
rxn4chemistry_wrapper.create_project('test_wrapper')
print(rxn4chemistry_wrapper.project_id)
```

### Reaction prediction

Running a reaction prediction is as simple as:

```python
response = rxn4chemistry_wrapper.predict_reaction(
    'BrBr.c1ccc2cc3ccccc3cc2c1'
)
results = rxn4chemistry_wrapper.get_predict_reaction_results(
    response['prediction_id']
)
print(results['response']['payload']['attempts'][0]['smiles'])
```

### Extracting actions from a paragraph describing a recipe

Extract the actions from a recipe:

```python
results = rxn4chemistry_wrapper.paragraph_to_actions(
    'To a stirred solution of '
    '7-(difluoromethylsulfonyl)-4-fluoro-indan-1-one (110 mg, '
    '0.42 mmol) in methanol (4 mL) was added sodium borohydride '
    '(24 mg, 0.62 mmol). The reaction mixture was stirred at '
    'ambient temperature for 1 hour.'
)
print(results['actions'])
```

### Retrosynthesis prediction

Predict a retrosynthetic pathway given a product:

```python
response = rxn4chemistry_wrapper.predict_automatic_retrosynthesis(
    'Brc1c2ccccc2c(Br)c2ccccc12'
)
results = rxn4chemistry_wrapper.get_predict_automatic_retrosynthesis_results(
    response['prediction_id']
)
print(results['status'])
# NOTE: upon 'SUCCESS' you can inspect the predicted retrosynthetic paths.
print(results['retrosynthetic_paths'][0])
```

See [here](./examples/diamond_light_source_covid19_candidates_retrosynthesis.ipynb) for a more comprehensive example.

## Examples

To learn more see the [examples](./examples).

## Documentation

The documentation is hosted [here](https://rxn4chemistry.github.io/rxn4chemistry/) using GitHub pages.
