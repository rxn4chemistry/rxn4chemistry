"""URL routes for IBM RXN for Chemistry API."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
import os

BASE_URL = 'https://rxn.res.ibm.com'
API_URL = os.path.join(BASE_URL, 'rxn/api/api/v1')
PROJECT_URL = os.path.join(API_URL, 'projects')
PREDICTIONS_URL = os.path.join(API_URL, 'predictions')
ATTEMPTS_URL = os.path.join(PROJECT_URL, '{project_id}', 'attempts')
RETROSYNTHESIS_URL = os.path.join(API_URL, 'retrosynthesis')
REACTION_PREDICTION_URL = os.path.join(PREDICTIONS_URL, 'pr')
REACTION_PREDICTION_RESULTS_URL = os.path.join(
    PREDICTIONS_URL, '{prediction_id}'
)
RETROSYNTHESIS_PREDICTION_URL = os.path.join(RETROSYNTHESIS_URL, 'rs')
RETROSYNTHESIS_PREDICTION_RESULTS_URL = os.path.join(
    RETROSYNTHESIS_URL, '{prediction_id}'
)
