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

### Reaction outcome prediction

Running a reaction outcome prediction is as simple as:

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


### Prediction of reaction properties (atom-to-atom mapping, reaction yield, ...)

Prediction of atom-to-atom mapping (see [paper](https://doi.org/10.1126/sciadv.abe4166)):
```python
response = rxn4chemistry_wrapper.predict_reaction_properties(
    reactions=[
        "CC(C)S.CN(C)C=O.Fc1cccnc1F.O=C([O-])[O-].[K+].[K+]>>CC(C)Sc1ncccc1F",
        "C1COCCO1.CC(C)(C)OC(=O)CONC(=O)NCc1cccc2ccccc12.Cl>>O=C(O)CONC(=O)NCc1cccc2ccccc12",
        "C=CCN=C=S.CNCc1ccc(C#N)cc1.NNC(=O)c1cn2c(n1)CCCC2>>C=CCN1C(C2=CN3CCCCC3=N2)=NN=C1N(C)CC1=CC=C(C#N)C=C1",
    ],
    ai_model="atom-mapping-2020",
)
for predicted_mapping_dict in response["response"]["payload"]["content"]:
    print(predicted_mapping_dict["value"])
```

Prediction of reaction yields (see [paper](https://doi.org/10.1088/2632-2153/abc81d)):
```python
response = rxn4chemistry_wrapper.predict_reaction_properties(
    reactions=[
        "Clc1ccccn1.Cc1ccc(N)cc1.O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F.COc1ccc(OC)c(P([C@]23C[C@H]4C[C@H](C[C@H](C4)C2)C3)[C@]23C[C@H]4C[C@H](C[C@H](C4)C2)C3)c1-c1c(C(C)C)cc(C(C)C)cc1C(C)C.CCN=P(N=P(N(C)C)(N(C)C)N(C)C)(N(C)C)N(C)C.Cc1cc(C)on1>>Cc1ccc(Nc2ccccn2)cc1",
        "Brc1ccccn1.Cc1ccc(N)cc1.O=S(=O)(O[Pd]1c2ccccc2-c2ccccc2N~1)C(F)(F)F.COc1ccc(OC)c(P([C@]23C[C@H]4C[C@H](C[C@H](C4)C2)C3)[C@]23C[C@H]4C[C@H](C[C@H](C4)C2)C3)c1-c1c(C(C)C)cc(C(C)C)cc1C(C)C.CCN=P(N=P(N(C)C)(N(C)C)N(C)C)(N(C)C)N(C)C.COC(=O)c1ccno1>>Cc1ccc(Nc2ccccn2)cc1",
    ],
    ai_model="yield-2020-08-10",
)
for predicted_yield_dict in response["response"]["payload"]["content"]:
    print(predicted_yield_dict["value"])
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

## Prediction of multiple reaction outcomes (in batch)

It is also possible to predict multiple forward reaction prediction outcomes in batch:

```python
response = rxn4chemistry_wrapper.predict_reaction_batch_topn(
    precursors_lists=[
        ["BrBr", "c1ccc2cc3ccccc3cc2c1"],
        ["BrBr", "c1ccc2cc3ccccc3cc2c1CCO"],
    ],
    topn=3,
)
# wait for the predictions to complete
time.sleep(2)
print(rxn4chemistry_wrapper.get_predict_reaction_batch_topn_results(response["task_id"]))
```

**NOTE:** the results for batch prediction are not stored permanently in our databases, so we strongly recommend to save them since they will expire.

## Enable logging

Logging by the library is disabled by default as it may interfere with programmatic uses.

In the very top of the `rxn4chemistry_tour.ipynb` example notebook you can see a line that enables all logging in the notebook.
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')
```
This may also enable logging from other libraries. If you wish to selectively enable the logs from `rxn4chemistry`, consider something like this:
```python
import logging
logger = logging.getLogger("rxn4chemistry")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s : %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
```

## Examples

To learn more see the [examples](./examples).

## Documentation

The documentation is hosted [here](https://rxn4chemistry.github.io/rxn4chemistry/) using GitHub pages.
