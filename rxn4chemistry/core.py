"""Core IBM RXN for Chemistry API module."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import copy
import logging
import requests
import json
from typing import Optional, List, Dict, Tuple
from .urls import (
    PROJECT_URL, ATTEMPTS_URL, REACTION_PREDICTION_URL,
    REACTION_PREDICTION_RESULTS_URL, RETROSYNTHESIS_PREDICTION_URL,
    RETROSYNTHESIS_PREDICTION_RESULTS_URL, RETROSYNTHESIS_SEQUENCE_PDF_URL,
    PARAGRAPH2ACTIONS_URL,
    SYNTHESIS_CREATION_FROM_SEQUENCE_URL, SYNTHESIS_STATUS_URL, SYNTHESIS_START_URL, SYNTHESIS_SPECTROMETER_REPORT_URL)
from .decorators import ibm_rxn_api_limits, response_handling
from .callbacks import (
    prediction_id_on_success, default_on_success,
    automatic_retrosynthesis_results_on_success,
    retrosynthesis_sequence_pdf,
    paragraph_to_actions_on_success,
    synthesis_id_on_success, synthesis_status_on_success, synthesis_analysis_report_pdf)

LOGGER = logging.getLogger('rxn4chemistry:core')


class RXN4ChemistryWrapper:
    """
    Python wrapper for IBM RXN for Chemistry to access the REST API requests.
    """

    def __init__(
        self,
        api_key: str,
        logger: Optional[logging.Logger] = None,
        project_id: Optional[str] = None
    ):
        """
        RXN4ChemistryWrapper constructor.

        Args:
            api_key (str): an API key to access the service.
            logger (logging.Logger, optional): a logger.
                Defaults to None, a.k.a using a default logger.
            project_id (str, optional): project identifier. Defaults to None.

        Examples:
            Initialize the wrapper by simply providing an API key:

            >>> from rxn4chemistry import RXN4ChemistryWrapper
            >>> rxn4chemistry_wrapper = RXN4ChemistryWrapper(api_key=api_key)
        """
        self._api_key = api_key
        self.project_id = project_id
        self.logger = logger if logger else LOGGER
        self.headers = self._construct_headers()

    def _construct_headers(self) -> dict:
        """
        Construct header, required for all requests.

        Returns:
            dict: dictionary containing the "Content-Type" and the
                "Authorization".
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': self._api_key
        }

    @response_handling(
        success_status_code=200, on_success=synthesis_id_on_success
    )
    @ibm_rxn_api_limits
    def create_synthesis_from_sequence(
        self,
        sequence_id: str
    ) -> requests.models.Response:
        """
        Create a new synthesis from a sequence identifier.

        A sequence id can be retrieved from the results of an automated retrosynthesis
        prediction.

        Args:
            sequence_id (str): a sequence identifier returned by
                predict_automatic_retrosynthesis_results.

        Returns:
            dict: dictionary containing the synthesis identifier and the
                response.

        Examples:
            Create a synthesis by providing the desired sequence identifier:

            >>> response = rxn4chemistry_wrapper.create_synthesis_from_sequence(
                '5dd273618sid4897af'
            )
        """
        if self.project_id is None:
            raise ValueError('Project identifier has to be set first.')
        data = {
            'sequenceId': sequence_id
        }
        response = requests.post(
            SYNTHESIS_CREATION_FROM_SEQUENCE_URL,
            headers=self.headers,
            data=json.dumps(data),
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200,
        on_success=synthesis_status_on_success
    )
    @ibm_rxn_api_limits
    def get_synthesis_status(
            self, synthesis_id: str
    ) -> requests.models.Response:
        """
        Get the status of a given synthesis based on its identifier.

        The provided synthesis identifier can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the the response.

        Examples:
            Create a synthesis by providing the desired sequence identifier:

            >>> response = rxn4chemistry_wrapper.get_synthesis_status(
                '5dd273618sid4897af'
            )
        """
        response = requests.get(
            SYNTHESIS_STATUS_URL.format(
                synthesis_id=synthesis_id
            ),
            headers=self.headers,
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200, on_success=synthesis_status_on_success
    )
    @ibm_rxn_api_limits
    def start_synthesis(
        self,
        synthesis_id: str
    ) -> requests.models.Response:
        """
        Start a synthesis on either on the robot or on the simulator.

        A robot (or simulator) key must be active in the user account in order
        for the query to be successful. The provided synthesis identifier can be
        obtained as a previous step by calling the create_synthesis_from_sequence() method.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the response.

        Examples:
            Start the synthesis with a given identifier:

            >>> response = rxn4chemistry_wrapper.start_synthesis(
                synthesis_id='5dd273618sid4897af'
            )
        """
        response = requests.post(
            SYNTHESIS_START_URL.format(synthesis_id=synthesis_id),
            headers=self.headers,
            cookies={}
        )
        return response

    def get_synthesis_plan(self, synthesis_id: str) -> Tuple[Dict, List, List]:
        """
        Return the synthesis tree for the given synthesis_id.

        This is a simplified version of get_synthesis_status which only includes
        synthesis related information and no meta data.
        It also returns a flattened list of all the actions involved in every
        step of the sequence.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            Tuple[Dict, List, List]: A dictionary representation of the synthesis
                tree and a flattened list containing all actions of the entire
                synthesis represented as dictionaries.

        Examples:
            Return the flattened list of actions for the given synthesis identifier:

            >>> result = rxn4chemistry_wrapper.get_tree_and_actions(
                synthesis_id='5dd273618sid4897af'
            )
        """
        response = self.get_synthesis_status(synthesis_id=synthesis_id)
        tree: Dict = copy.deepcopy(response['response']['payload']['sequences'][0]['tree'])

        def post_order_tree_traversal(tree: Dict) -> List[Dict]:
            result = []
            if 'children' in tree:
                for child in tree['children']:
                    result.extend(post_order_tree_traversal(child))
            if tree:
                result.append(tree)
            return result

        ordered_tree_nodes = post_order_tree_traversal(tree=tree)

        keys_to_keep = ['id', 'smiles', 'actions', 'children']
        flattened_actions = []

        for node in ordered_tree_nodes:
            [node.pop(key) for key in list(node.keys()) if key not in keys_to_keep]
            flattened_actions.extend(node['actions'])
        return tree, ordered_tree_nodes, flattened_actions

    def get_synthesis_actions_with_spectrometer_pdf(
        self,
        synthesis_id: str
    ) -> List[Dict]:
        """
        Get a list of actions which have a spectrometer pdf ready for download.

        Args:
            synthesis_id (str): synthesis identifier.

        Returns:
            List[Dict]: a list of all actions in the synthesis which have a
                spectrometer pdf ready for download

        Examples:
            Get the list of actions which have a report pdf ready for download:

            >>> rxn4chemistry_wrapper.get_synthesis_actions_with_spectrometer_pdf(
                '5e788ae548260b770105ecf4'
            )
        """
        synthesis_tree, ordered_tree_nodes, actions = self.get_synthesis_plan(
            synthesis_id=synthesis_id
        )
        result = []
        for node in ordered_tree_nodes:
            for action_index, action in enumerate(node['actions']):
                if action['hasSpectrometerPdf']:
                    result.append(
                        {
                            'synthesis_id': synthesis_id,
                            'node_id': node['id'],
                            'action_index': action_index
                        }
                    )
        return result

    @response_handling(
        success_status_code=200,
        on_success=synthesis_analysis_report_pdf
    )
    @ibm_rxn_api_limits
    def get_synthesis_analysis_report_pdf(
        self,
        synthesis_id: str,
        node_id: str,
        action_index: int
    ) -> requests.models.Response:
        """
        Get the spectrometer .pdf report for a given synthesis identifier,
        node identifier and action index.

        Args:
            synthesis_id (str): identifier of the synthesis.
            node_id (str): identifier of the node (corresponds to a reaction
                in the synthesis tree).
            action_index (int): corresponds to the index of the specific
                analysis action in the node.

        Returns:
            dict: dictionary containing the .pdf report.

        Examples:
            Get a .pdf report providing the synthesis identifier, node identifier and
            action index:

            >>> rxn4chemistry_wrapper.get_synthesis_analysis_report_pdf(
                synthesis_id='5e788ae548260b770105ecf4',
                node_id='5ecb86cx6776vx1234fsd',
                action_index=5
            )
            {...}
        """
        response = requests.get(
            SYNTHESIS_SPECTROMETER_REPORT_URL.format(
                synthesis_id=synthesis_id,
                node_id=node_id,
                action_index=action_index
            ),
            headers=self.headers,
            cookies={}
        )
        return response
