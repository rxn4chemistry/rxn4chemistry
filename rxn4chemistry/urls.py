"""URL routes for IBM RXN for Chemistry API."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

BASE_URL = 'https://rxn.res.ibm.com'
API_URL = '{}/{}'.format(BASE_URL, 'rxn/api/api/v1')
PROJECT_URL = '{}/{}'.format(API_URL, 'projects')
PREDICTIONS_URL = '{}/{}'.format(API_URL, 'predictions')
ATTEMPTS_URL = '{}/{}/{}'.format(PROJECT_URL, '{project_id}', 'attempts')
RETROSYNTHESIS_URL = '{}/{}'.format(API_URL, 'retrosynthesis')
REACTION_PREDICTION_URL = '{}/{}'.format(PREDICTIONS_URL, 'pr')
REACTION_PREDICTION_RESULTS_URL = '{}/{}'.format(
    PREDICTIONS_URL, '{prediction_id}'
)
RETROSYNTHESIS_PREDICTION_URL = '{}/{}'.format(RETROSYNTHESIS_URL, 'rs')
RETROSYNTHESIS_PREDICTION_RESULTS_URL = '{}/{}'.format(
    RETROSYNTHESIS_URL, '{prediction_id}'
)
RETROSYNTHESIS_PREDICTION_RESULTS_URL = '{}/{}'.format(
    RETROSYNTHESIS_URL, '{prediction_id}'
)
RETROSYNTHESIS_SEQUENCE_PDF_URL = '{}/sequences/{}/download-pdf'.format(
    RETROSYNTHESIS_PREDICTION_RESULTS_URL, '{sequence_id}'
)
PARAGRAPH2ACTIONS_URL = '{}/{}'.format(
    API_URL, 'paragraph-actions'
)
