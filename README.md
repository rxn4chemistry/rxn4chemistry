# Python wrapper for the IBM RXN for Chemistry API

[![Actions tests](https://github.com/rxn4chemistry/rxn4chemistry/actions/workflows/ci.yml/badge.svg)](https://github.com/rxn4chemistry/rxn4chemistry/actions)
[![PyPI version](https://badge.fury.io/py/RXN4Chemistry.svg)](https://badge.fury.io/py/RXN4Chemistry)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rxn4chemistry/rxn4chemistry/main)

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

By default, the wrapper connects to the [https://rxn.res.ibm.com](https://rxn.res.ibm.com) server. This can be overriden by setting an environment variable.
To set a different url, simply do:

```console
export RXN4CHEMISTRY_BASE_URL="https://some.other.rxn.server"
```

The base url can be directly set when instantiating the RXN4ChemistryWrapper (this will overwrite the environment variable):

```python
api_key = 'API_KEY'
from rxn4chemistry import RXN4ChemistryWrapper

rxn4chemistry_wrapper = RXN4ChemistryWrapper(api_key=api_key, base_url='https://some.other.rxn.server')
# or set it afterwards
# rxn4chemistry_wrapper = RXN4ChemistryWrapper(api_key=api_key)
# rxn4chemistry_wrapper.set_base_url('https://some.other.rxn.server')
```

### Create a project

Get your API key from [here](https://rxn.res.ibm.com/rxn/user/profile) and build the wrapper:

```python
api_key = 'API_KEY'
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

### Biocatalysed retrosynthesis prediction

Predict a biocatalysed retrosynthetic pathway given a product by specifying the model trained on biocatalysed reactions:

```python
response = rxn4chemistry_wrapper.predict_automatic_retrosynthesis(
    'OC1C(O)C=C(Br)C=C1', ai_model='enzymatic-2021-04-16'
)
results = rxn4chemistry_wrapper.get_predict_automatic_retrosynthesis_results(
    response['prediction_id']
)
print(results['status'])
# NOTE: upon 'SUCCESS' you can inspect the predicted retrosynthetic paths.
print(results['retrosynthetic_paths'][0])
```

### Create a synthesis and start it on the robot (or simulator)

Create a synthesis from a retrosynthesis sequence:

```python
# Each retrosynthetic path predicted has a unique sequence_id that can
# be used to create a new synthesis
response = rxn4chemistry_wrapper.create_synthesis_from_sequence(
    sequence_id=results['retrosynthetic_paths'][0]['sequenceId']
)
print(response['synthesis_id'])

# get the entire list of actions for the entire synthesis, as well as a tree representation
synthesis_tree, ordered_tree_nodes, ordered_list_of_actions = rxn4chemistry_wrapper.get_synthesis_plan(
    synthesis_id=response['synthesis_id']
)
for action in ordered_list_of_actions:
    print(action)

synthesis_status_result = rxn4chemistry_wrapper.start_synthesis(
    synthesis_id=response['synthesis_id']
)
print(synthesis_status_result['status'])

synthesis_status_result = rxn4chemistry_wrapper.get_synthesis_status(
    synthesis_id=response['synthesis_id']
)
print(synthesis_status_result['status'])
```

## Forward prediction in batch

It is possible to run a batch of forward reaction predictions without linking them to a project:

```python
response = rxn4chemistry_wrapper.predict_reaction_batch(precursors_list=['BrBr.c1ccc2cc3ccccc3cc2c1', 'Cl.c1ccc2cc3ccccc3cc2c1']*5)
# wait for the predictions to complete
time.sleep(2)
print(rxn4chemistry_wrapper.get_predict_reaction_batch_results(response["task_id"]))
```

**NOTE:** the results for batch prediction are not stored permanently in our databases, so we strongly recommend to save them since they will expire.

## Examples

To learn more see the [examples](./examples).

## Documentation

The documentation is hosted [here](https://rxn4chemistry.github.io/rxn4chemistry/) using GitHub pages.
