"""URL routes for IBM RXN for Chemistry API."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
import os

BASE_URL = os.getenv('RXN4CHEMISTRY_BASE_URL', 'https://rxn.res.ibm.com')
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
RETROSYNTHESIS_SEQUENCE_PDF_URL = '{}/sequences/{}/download-pdf'.format(
    RETROSYNTHESIS_PREDICTION_RESULTS_URL, '{sequence_id}'
)
PARAGRAPH2ACTIONS_URL = '{}/{}'.format(
    API_URL, 'paragraph-actions'
)
SYNTHESIS_URL = '{}/{}'.format(API_URL, 'synthesis')
SYNTHESIS_CREATION_FROM_SEQUENCE_URL = '{}/{}'.format(SYNTHESIS_URL, 'create-from-sequence')
SYNTHESIS_START_URL = '{}/{}/{}'.format(SYNTHESIS_URL, '{synthesis_id}', 'start')
SYNTHESIS_STATUS_URL = '{}/{}'.format(SYNTHESIS_URL, '{synthesis_id}')
SYNTHESIS_SPECTROMETER_REPORT_URL = '{}/{}/node/{}/action/{}/spectrometer-report'.format(
    SYNTHESIS_URL, '{synthesis_id}', '{node_id}', '{action_index}'
)
SYNTHESIS_PATCH_NODE_ACTIONS_URL = '{}/{}/{}/{}'.format(
    SYNTHESIS_URL, '{synthesis_id}', 'node', '{node_id}'
)
