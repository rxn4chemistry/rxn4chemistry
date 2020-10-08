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
            Initialize the wrapper by simply providing an API key.

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

    @response_handling(success_status_code=201, on_success=default_on_success)
    @ibm_rxn_api_limits
    def create_project(
        self,
        name: str,
        invitations: list = [],
        set_project: bool = True
    ) -> requests.models.Response:
        """
        Create new project on platform and set the project id,
        which is required to predict chemical reactions.

        Args:
            name (str): name of the project.
            invitations (list, optional): list of invitations for the project.
                Defaults to [], a.k.a. no invitations.
            set_project (bool, optional): wheter the created project is set.
                Defaults to True.

        Returns:
            dict: dictionary built from the JSON response. Empty in case of
            errors.

        Examples:
            Create a project using the wrapper.

            >>> rxn4chemistry_wrapper.create_project('test')
        """
        data = {'name': name, 'invitations': invitations}
        response = requests.post(
            PROJECT_URL,
            headers=self.headers,
            data=json.dumps(data),
            cookies={}
        )

        if set_project and response.status_code == 201:
            self.set_project(response.json()['payload']['id'])

        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def list_all_projects(self) -> requests.models.Response:
        """
        Get a list of all projects.

        Returns:
            dict: dictionary listing the projects.

        Examples:
            Retrieve all the projects for the API key used to construct the
            wrapper.

            >>> rxn4chemistry_wrapper.list_all_projects()
            {...}
        """
        response = requests.get(PROJECT_URL, headers=self.headers, cookies={})
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def list_all_attempts_in_project(
        self,
        project_id: str = None,
        page: int = 0,
        size: int = 8,
        ascending_creation_order: bool = True
    ) -> requests.models.Response:
        """
        Get a list of all the attempts in the set project.

        Args:
            project_id (str, optional): project identifier. Defaults to None,
                a.k.a., use the currently set project.
            page (int, optional): page to list attempts from. Defaults to 0.
            size (int, optional): number of elements per page. Defaults to 8.
            ascending_creation_order (bool, optional): sort attempts by
                ascending creation date. Defaults to True.

        Returns:
            dict: dictionary listing the attempts.

        Examples:
            Retrieve all the attempts for currently set project identifier.

            >>> rxn4chemistry_wrapper.list_all_attempts_in_project()
            {...}
        """
        if project_id is None:
            project_id = self.project_id
        payload = {
            'raw': {},
            'page':
                page,
            'size':
                size,
            'sort':
                'createdOn|{}'.
                format('ASC' if ascending_creation_order else 'DESC')
        }
        response = requests.get(
            ATTEMPTS_URL.format(project_id=project_id),
            headers=self.headers,
            cookies={},
            params=payload
        )
        return response

    def set_project(self, project_id: str):
        """
        Set project using the project id.
        The project_id can also be found in the url of the project.

        Args:
            project_id (str): project identifier.

        Examples:
            Set a project for the wrapper instantiated.

            >>> rxn4chemistry_wrapper.set_project('PROJECT_ID')
        """
        self.logger.info('Set project id to {}'.format(project_id))
        self.project_id = project_id

    def set_api_key(self, api_key: str):
        """
        Set the API key.
        This method also rebuilds the headers.

        Args:
            api_key (str): an API key to access the service.

        Examples:
            Set an API key.

            >>> rxn4chemistry_wrapper.set_api_key('API_KEY')
        """
        self.logger.info('Set API key to {}'.format(api_key))
        self._api_key = api_key
        self.headers = self._construct_headers()

    @response_handling(
        success_status_code=200, on_success=prediction_id_on_success
    )
    @ibm_rxn_api_limits
    def predict_reaction(
        self,
        precursors: str,
        prediction_id: str = None
    ) -> requests.models.Response:
        """
        Launch prediction given precursors SMILES.

        Args:
            precursors (str): a reaction SMILES.
            prediction_id (str, optional): prediction identifier. Defaults to
                None, a.k.a., run an independent prediction.

        Returns:
            dict: dictionary containing the prediction identifier and the
            response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a reaction by providing the reaction SMILES.

            >>> response = rxn4chemistry_wrapper.predict_reaction(
                'BrBr.c1ccc2cc3ccccc3cc2c1'
            )
        """
        if self.project_id is None:
            raise ValueError('Project identifier has to be set first.')
        payload = {'projectId': self.project_id}
        if prediction_id is not None:
            payload['predictionId'] = prediction_id
        data = {'reactants': precursors}
        response = requests.post(
            REACTION_PREDICTION_URL,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload
        )
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def get_predict_reaction_results(
        self, prediction_id: str
    ) -> requests.models.Response:
        """
        Get the predict reaction results for a prediction_id.

        Args:
            prediction_id (str): prediction identifier.

        Returns:
            dict: dictionary containing the prediction results.

        Examples:
            Get results from a reaction prediction by providing the prediction
            identifier.

            >>> rxn4chemistry_wrapper.get_predict_reaction_results(
                response['response']['payload']['id']
                # or response['prediction_id']
            )
            {...}
        """
        response = requests.get(
            REACTION_PREDICTION_RESULTS_URL.format(
                prediction_id=prediction_id
            ),
            headers=self.headers,
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200, on_success=prediction_id_on_success
    )
    @ibm_rxn_api_limits
    def predict_automatic_retrosynthesis(
        self,
        product: str,
        availability_pricing_threshold: int = 0,
        available_smiles: Optional[str] = None,
        exclude_smiles: Optional[str] = None,
        exclude_substructures: Optional[str] = None,
        exclude_target_molecule: bool = True,
        fap: float = 0.6,
        max_steps: int = 3,
        nbeams: int = 10,
        pruning_steps: int = 2
    ) -> requests.models.Response:
        """
        Launch automated retrosynthesis prediction given a product SMILES.

        Args:
            product (str): a prouct SMILES.
            availability_pricing_threshold (int, optional): maximum price in
                USD per mg/ml of commercially available compounds that will be
                considered available precursors for the retrosynthesis.
                Defaults to 0, a.k.a., no threshold.
            available_smiles (str, optional): SMILES of molecules available as
                precursors. Defaults to None, a.k.a., use the default ones.
                Multiple molecules can be provided separating them via ".".
            exclude_smiles (str, optional): SMILES of molecules to exclude
                from the set of precursors. Defaults to None, a.k.a., no
                excluded molecules. Multiple molecules can be provided
                separating them via ".".
            exclude_substructures (str, optional): SMILES of substructures to
                exclude from precursors
                Defaults to None, a.k.a., no excluded substructures. Multiple
                molecules can be provided separating them via ".".
            exclude_target_molecule (bool, optional): whether the product has
                to be excluded. Defaults to True.
            fap (float, optional): forward acceptance probability. Every
                retrosynthetic step is evaluated with the forward prediction
                model. The step is retained if the the forward confidence is
                greater than FAP. Defaults to 0.6.
            max_steps (int, optional): maximum number of retrosynthetic steps.
                Defaults to 3.
            nbeams (int, optional): maximum number of beams exploring the
                hyper-tree. Defaults to 10.
            pruning_steps (int, optional): number of interval steps to prune
                the explored hyper-tree. Defaults to 2.

        Returns:
            dict: dictionary containing the prediction identifier and the
            response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a retrosynthesis by providing the product SMILES.

            >>> response = rxn4chemistry_wrapper.predict_automatic_retrosynthesis(
                'Brc1c2ccccc2c(Br)c2ccccc12'
            )
        """
        if self.project_id is None:
            raise ValueError('Project identifier has to be set first.')
        payload = {'projectId': self.project_id}
        data = {
            'isinteractive': False,
            'parameters':
                {
                    'availability_pricing_threshold':
                        availability_pricing_threshold,
                    'available_smiles':
                        available_smiles,
                    'exclude_smiles':
                        exclude_smiles,
                    'exclude_substructures':
                        exclude_substructures,
                    'exclude_target_molecule':
                        exclude_target_molecule,
                    'fap':
                        fap,
                    'max_steps':
                        max_steps,
                    'nbeams':
                        nbeams,
                    'pruning_steps':
                        pruning_steps
                },
            'product': product
        }
        response = requests.post(
            RETROSYNTHESIS_PREDICTION_URL,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload
        )
        return response

    @response_handling(
        success_status_code=200,
        on_success=automatic_retrosynthesis_results_on_success
    )
    @ibm_rxn_api_limits
    def get_predict_automatic_retrosynthesis_results(
        self, prediction_id: str
    ) -> requests.models.Response:
        """
        Get the predict automatic retrosynthesis results for a prediction_id.

        Args:
            prediction_id (str): prediction identifier.

        Returns:
            dict: dictionary containing the prediction results.

        Examples:
            Get results from an automatic retrosynthesis prediction by
            providing the prediction identifier.

            >>> rxn4chemistry_wrapper.get_predict_automatic_retrosynthesis_results(
                response['response']['payload']['id']
                # or response['prediction_id']
            )
            {...}
        """
        response = requests.get(
            RETROSYNTHESIS_PREDICTION_RESULTS_URL.format(
                prediction_id=prediction_id
            ),
            headers=self.headers,
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200,
        on_success=retrosynthesis_sequence_pdf
    )
    @ibm_rxn_api_limits
    def get_retrosynthesis_sequence_pdf(
        self, prediction_id: str, sequence_id: str
    ) -> requests.models.Response:
        """
        Get the .pdf report for a given retrosynthesis sequence.

        Args:
            prediction_id (str): prediction identifier.
            sequence_id (str): sequence identifier.

        Returns:
            dict: dictionary containing the .pdf report.

        Examples:
            Get a .pdf report providing the prediction identifier and a
            sequence identifier.

            >>> rxn4chemistry_wrapper.get_retrosynthesis_sequence_pdf(
                response['response']['payload']['id'],
                '5e788ae548260b770105ecf4'
            )
            {...}
        """
        response = requests.get(
            RETROSYNTHESIS_SEQUENCE_PDF_URL.format(
                prediction_id=prediction_id,
                sequence_id=sequence_id
            ),
            headers=self.headers,
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200,
        on_success=paragraph_to_actions_on_success
    )
    @ibm_rxn_api_limits
    def paragraph_to_actions(
        self, paragraph: str
    ) -> requests.models.Response:
        """
        Get the actions from a paragraph describing a recipe.

        Args:
            paragraph (str): paragraph describing a recipe.

        Returns:
            dict: dictionary containing the actions.

        Examples:
            Get actions from a paragraph.

            >>> results = rxn4chemistry_wrapper.paragraph_to_actions(
                'To a stirred solution of '
                '7-(difluoromethylsulfonyl)-4-fluoro-indan-1-one (110 mg, '
                '0.42 mmol) in methanol (4 mL) was added sodium borohydride '
                '(24 mg, 0.62 mmol). The reaction mixture was stirred at '
                'ambient temperature for 1 hour. '
            )
            >>> results['actions']
            ['MAKESOLUTION with 7-(difluoromethylsulfonyl)-4-fluoro-indan-1-one (110 mg, 0.42 mmol) and methanol (4 mL)',
            'ADD SLN',
            'ADD sodium borohydride (24 mg, 0.62 mmol)',
            'STIR for 1 hour at ambient temperature']
        """
        data = {'paragraph': paragraph}
        response = requests.post(
            PARAGRAPH2ACTIONS_URL,
            headers=self.headers,
            data=json.dumps(data).encode(),
            cookies={}
        )
        return response

    @response_handling(
        success_status_code=200, on_success=synthesis_id_on_success
    )
    @ibm_rxn_api_limits
    def create_synthesis_from_sequence(
        self,
        sequence_id: str
    ) -> requests.models.Response:
        """
        Create a new synthesis from a sequence id. A sequence id
        can be retrieved from the results of an automated retrosynthesis
        prediction.

        Args:
            sequence_id (str): a sequence id returned by
                predict_automatic_retrosynthesis_results.

        Returns:
            dict: dictionary containing the synthesis identifier and the
            response.

        Examples:
            Create a synthesis by providing the desired sequence id.

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
        Get the status of a given synthesis based on its id. The
        provided synthesis id can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method

        Args:
            synthesis_id (str): a synthesis id returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the the
            response.

        Examples:
            Create a synthesis by providing the desired sequence id.

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
        Start a synthesis on either on the robot or on the
        simulator. A robot (or simulator) key must be active in the
        user account in order for the query to be successful. The
        provided synthesis id can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method

        Args:
            synthesis_id (str): a synthesis id returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the response.

        Examples:
            Start the synthesis with a given id.

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
        This is a simplified version of get_synthesis_status
        which only includes synthesis related information and
        no meta data. It also returns a flattened list of all
        the actions involved in every step of the sequence.


        Args:
            synthesis_id (str): a synthesis id returned by
                create_synthesis_from_sequence() method.

        Returns:
            Tuple[Dict, List, List]: A dictionary representation of the
                synthesis tree and a flattened list containing all
                actions of the entire synthesis represented as
                dictionaries.

        Examples:
            Return the flattened list of actions for the given synthesis id

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
        Get a list of actions which have a spectrometer
        pdf ready for download.

        Args:
            synthesis_id (str): synthesis identifier.

        Returns:
            List[Dict]: A list of all actions in the synthesis
                which have a spectrometer pdf ready for download

        Examples:
            Get the list of actions which have a report pdf
            ready for download

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
        Get the spectrometer .pdf report for a given synthesis id,
        node id and action index.

        Args:
            synthesis_id (str): id of the synthesis
            node_id (str): id of the node (corresponds to a reaction
                in the synthesis tree)
            action_index (int): corresponds to the index of the
                specific analysis action in the node

        Returns:
            dict: dictionary containing the .pdf report.

        Examples:
            Get a .pdf report providing the synthesis id, node id and
            action index.

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
