"""Core IBM RXN for Chemistry API module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import requests

from .callbacks import (
    automatic_retrosynthesis_results_on_success,
    default_on_success,
    model_listing_on_success,
    paragraph_to_actions_on_success,
    predict_reaction_batch_on_success,
    prediction_id_on_success,
    reaction_settings_on_success,
    retrosynthesis_sequence_pdf,
    synthesis_analysis_report_pdf,
    synthesis_execution_id_on_success,
    synthesis_execution_status_on_success,
    synthesis_id_on_success,
    synthesis_on_success,
    task_id_on_success,
)
from .decorators import ibm_rxn_api_limits, response_handling
from .urls import RXN4ChemistryRoutes

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def post_order_tree_traversal(tree: Dict) -> List[Dict]:
    result = []
    if "children" in tree:
        for child in tree["children"]:
            result.extend(post_order_tree_traversal(child))
    if tree:
        result.append(tree)
    return result


class RXN4ChemistryWrapper:
    """
    Python wrapper for IBM RXN for Chemistry to access the REST API requests.
    """

    def __init__(
        self,
        api_key: str,
        project_id: Optional[str] = None,
        base_url: Optional[str] = None,
        batch_executor_base_url: Optional[str] = None,
    ):
        """
        RXN4ChemistryWrapper constructor.

        Args:
            api_key (str): an API key to access the service.
            project_id (str, optional): project identifier. Defaults to None.
            base_url (str, optional): base url for the service. If not provided it will default to
                the environment variable RXN4CHEMISTRY_BASE_URL or https://rxn.res.ibm.com.
            batch_executor_base_url (str, optional): base url for the batch executor service. If not provided
                it will default to the environment variable BATCH_EXECUTOR_BASE_URL.

        Examples:
            Initialize the wrapper by simply providing an API key:

            >>> from rxn4chemistry import RXN4ChemistryWrapper
            >>> rxn4chemistry_wrapper = RXN4ChemistryWrapper(api_key=api_key)
        """
        self._api_key = api_key
        self.project_id = project_id
        self.headers = self._construct_headers()
        self.routes = RXN4ChemistryRoutes(base_url, batch_executor_base_url)

    def set_base_url(self, base_url: str) -> None:
        """
        Set base url for the RXN for Chemistry service.

        Args:
            base_url (str): base url for the service to set.
        """
        self.routes.base_url = base_url

    def set_batch_executor_base_url(self, batch_executor_base_url: str) -> None:
        """
        Set base url for the RXN batch-executor service.

        Args:
            batch_executor_base_url (str): base url for the service to set.
        """
        self.routes.batch_executor_base_url = batch_executor_base_url

    def _construct_headers(self) -> dict:
        """
        Construct header, required for all requests.

        Returns:
            dict: dictionary containing the "Content-Type" and the
                "Authorization".
        """
        return {"Content-Type": "application/json", "Authorization": self._api_key}

    @response_handling(success_status_code=201, on_success=default_on_success)
    @ibm_rxn_api_limits
    def create_project(
        self, name: str, invitations: list = [], set_project: bool = True
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
            Create a project using the wrapper:

            >>> rxn4chemistry_wrapper.create_project('test')
        """
        data = {"name": name, "invitations": invitations}
        response = requests.post(
            self.routes.project_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )

        if set_project and response.status_code == 201:
            self.set_project(response.json()["payload"]["id"])

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
            wrapper:

            >>> rxn4chemistry_wrapper.list_all_projects()
            {...}
        """
        response = requests.get(
            self.routes.project_url, headers=self.headers, cookies={}
        )
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def list_all_attempts_in_project(
        self, project_id: Optional[str] = None, page: int = 0, size: int = 8
    ) -> requests.models.Response:
        """
        Get a list of all the forward prediction attempts in the set project.

        Args:
            project_id (str, optional): project identifier. Defaults to None,
                a.k.a., use the currently set project.
            page (int, optional): page to list attempts from. Defaults to 0.
            size (int, optional): number of elements per page. Defaults to 8.

        Returns:
            dict: dictionary listing the attempts.

        Examples:
            Retrieve all the forward reaction prediction attempts for currently
                set project identifier:

            >>> rxn4chemistry_wrapper.list_all_attempts_in_project()
            {...}
        """
        if project_id is None:
            project_id = self.project_id
        payload = {"raw": {}, "page": page, "size": size}
        response = requests.get(
            self.routes.attempts_url.format(project_id=project_id),
            headers=self.headers,
            cookies={},
            params=payload,
        )
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def list_all_retro_attempts_in_project(
        self, project_id: Optional[str] = None, page: int = 0, size: int = 8
    ) -> requests.models.Response:
        """
        Get a list of all the retrosynthesis attempts in the set project.

        Args:
            project_id (str, optional): project identifier. Defaults to None,
                a.k.a., use the currently set project.
            page (int, optional): page to list attempts from. Defaults to 0.
            size (int, optional): number of elements per page. Defaults to 8.

        Returns:
            dict: dictionary listing the retrosynthesis attempts.

        Examples:
            Retrieve all the retrosynthesis attempts for currently set project
                identifier:

            >>> rxn4chemistry_wrapper.list_all_retro_attempts_in_project()
            {...}
        """
        if project_id is None:
            project_id = self.project_id
        payload = {"raw": {}, "page": page, "size": size}
        response = requests.get(
            self.routes.retro_attempts_url.format(project_id=project_id),
            headers=self.headers,
            cookies={},
            params=payload,
        )
        return response

    def set_project(self, project_id: str):
        """
        Set project using the project id.

        The project_id can also be found in the url of the project.

        Args:
            project_id (str): project identifier.

        Examples:
            Set a project for the wrapper instantiated:

            >>> rxn4chemistry_wrapper.set_project('PROJECT_ID')
        """
        logger.info("Set project id to {}".format(project_id))
        self.project_id = project_id

    def set_api_key(self, api_key: str):
        """
        Set the API key.

        This method also rebuilds the headers.

        Args:
            api_key (str): an API key to access the service.

        Examples:
            Set an API key:

            >>> rxn4chemistry_wrapper.set_api_key('API_KEY')
        """
        logger.info("Set API key to {}".format(api_key))
        self._api_key = api_key
        self.headers = self._construct_headers()

    @response_handling(success_status_code=200, on_success=model_listing_on_success)
    @ibm_rxn_api_limits
    def list_models(self) -> requests.models.Response:
        """
        Get the models for the project that is currently configured.

        Returns:
            dict: dictionary containing the available models.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Get list of models supported in the project considered:

            >>> rxn4chemistry_wrapper.list_models()
            {...}
        """
        if self.project_id is None:
            raise ValueError("Project identifier has to be set first.")

        response = requests.get(
            self.routes.project_models_url,
            headers=self.headers,
            params={"project_id": self.project_id},
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=prediction_id_on_success)
    @ibm_rxn_api_limits
    def predict_reaction(
        self,
        precursors: str,
        ai_model: str = "2020-08-10",
    ) -> requests.models.Response:
        """
        Launch prediction given precursors SMILES.

        Args:
            precursors (str): precursor SMILES separated with a '.'.
            ai_model (str, optional): model release. Defaults to
                '2020-08-10'.

        Returns:
            dict: dictionary containing the prediction identifier and the
            response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a reaction by providing the reaction SMILES:

            >>> response = rxn4chemistry_wrapper.predict_reaction(
                'BrBr.c1ccc2cc3ccccc3cc2c1'
            )
        """
        if self.project_id is None:
            raise ValueError("Project identifier has to be set first.")
        payload = {"projectId": self.project_id, "aiModel": ai_model}
        data = {"reactants": precursors, "aiModel": ai_model}
        response = requests.post(
            self.routes.reaction_prediction_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload,
        )
        return response

    @response_handling(success_status_code=200, on_success=prediction_id_on_success)
    @ibm_rxn_api_limits
    def predict_reaction_alternative_results(
        self,
        prediction_id: str,
        precursors: str,
        ai_model: str = "2020-08-10",
    ) -> requests.models.Response:
        """
        Generate alternative predict reaction results for a prediction_id.

        Args:
            prediction_id (str): prediction identifier.
            precursors (str): precursor SMILES separated with a '.'.
            ai_model (str, optional): model release. Defaults to
                '2020-08-10'.

        Returns:
            dict: dictionary containing the prediction results.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Generate alternative results from a reaction prediction by providing the prediction
            identifier and the prediction inputs:

            >>> rxn4chemistry_wrapper.predict_reaction_alternative_results(
                prediction_id=response['response']['payload']['id'],  # or response['prediction_id']
                precursors='BrBr.c1ccc2cc3ccccc3cc2c1'
            )
            {...}
        """
        if self.project_id is None:
            raise ValueError("Project identifier has to be set first.")
        payload = {"projectId": self.project_id, "predictionId": prediction_id}
        data = {"reactants": precursors, "aiModel": ai_model}
        response = requests.post(
            self.routes.reaction_prediction_alternative_results_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload,
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
            identifier:

            >>> rxn4chemistry_wrapper.get_predict_reaction_results(
                response['response']['payload']['id']
                # or response['prediction_id']
            )
            {...}
        """
        response = requests.get(
            self.routes.reaction_prediction_results_url.format(
                prediction_id=prediction_id
            ),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=task_id_on_success)
    @ibm_rxn_api_limits
    def predict_reaction_batch(
        self, precursors_list: List[str], ai_model: str = "2020-08-10"
    ) -> requests.models.Response:
        """
        Launch prediction given precursors SMILES.

        Args:
            precursors_list (List[str]): list of precursor SMILES separated with a '.'.
            ai_model (str, optional): model release. Defaults to
                '2020-08-10'.

        Returns:
            dict: dictionary containing the
            response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a reaction by providing the reaction SMILES and get task identifier
            and status:

            >>> response = rxn4chemistry_wrapper.predict_reaction_batch(
                ['BrBr.c1ccc2cc3ccccc3cc2c1', 'Cl.c1ccc2cc3ccccc3cc2c1']
            )
        """
        payload = {"aiModel": ai_model}
        data = {"reactants": precursors_list, "aiModel": ai_model}
        response = requests.post(
            self.routes.reaction_prediction_batch_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload,
        )
        return response

    @response_handling(
        success_status_code=200, on_success=predict_reaction_batch_on_success
    )
    @ibm_rxn_api_limits
    def get_predict_reaction_batch_results(
        self, task_id: str
    ) -> requests.models.Response:
        """
        Get the predict reaction batch results for a task_id.

        Args:
            task_id (str): task identifier.

        Returns:
            dict: dictionary containing the prediction results.

        Examples:
            Get results from a reaction prediction by providing the prediction
            identifier:

            >>> rxn4chemistry_wrapper.get_predict_reaction_batch_results(
                response["task_id"]
            )
            {...}
        """
        response = requests.get(
            self.routes.reaction_prediction_batch_results_url.format(task_id=task_id),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=task_id_on_success)
    @ibm_rxn_api_limits
    def predict_reaction_batch_topn(
        self, precursors_lists: List[List[str]], topn: int, ai_model: str = "2020-08-10"
    ) -> requests.models.Response:
        """
        Launch prediction of multiple outcomes for batch of reactions given precursors SMILES.

        Args:
            precursors_lists: lists of precursor SMILES (one list of precursors per reaction).
            topn: number of predictions to make per reaction.
            ai_model: model release.

        Returns:
            dict: dictionary containing the response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a reaction batch (with multiple predictions) by providing the
            lists of precursors and get task identifier
            and status:

            >>> response = rxn4chemistry_wrapper.predict_reaction_batch_topn(
            ...     ['BrBr', 'c1ccc2cc3ccccc3cc2c1'], ['Cl', 'c1ccc2cc3ccccc3cc2c1'],
            ...     topn=4
            ... )
        """
        data = {"precursors_lists": precursors_lists, "topn": topn, "aiModel": ai_model}
        response = requests.post(
            self.routes.reaction_prediction_batch_topn_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )
        return response

    @response_handling(
        success_status_code=200, on_success=predict_reaction_batch_on_success
    )
    @ibm_rxn_api_limits
    def get_predict_reaction_batch_topn_results(
        self, task_id: str
    ) -> requests.models.Response:
        """
        Get the results for a batch with multiple predictions for a task_id.

        Args:
            task_id: task identifier.

        Returns:
            dict: dictionary containing the prediction results.

        Examples:
            Get results from a reaction prediction by providing the prediction
            identifier:

            >>> rxn4chemistry_wrapper.get_predict_reaction_batch_topn_results(
            ...     response["task_id"]
            ... )
            ... {...}
        """
        response = requests.get(
            self.routes.reaction_prediction_batch_topn_results_url.format(
                task_id=task_id
            ),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=prediction_id_on_success)
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
        pruning_steps: int = 2,
        ai_model: str = "2020-07-01",
    ) -> requests.models.Response:
        """
        Launch automated retrosynthesis prediction given a product SMILES.

        Args:
            product (str): a prouct SMILES.
            availability_pricing_threshold (int, optional): maximum price in
                USD per g/ml of commercially available compounds that will be
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
            ai_model (str, optional): model release. Defaults to
                '2020-07-01'.

        Returns:
            dict: dictionary containing the prediction identifier and the
            response.

        Raises:
            ValueError: in case self.project_id is not set.

        Examples:
            Predict a retrosynthesis by providing the product SMILES:

            >>> response = rxn4chemistry_wrapper.predict_automatic_retrosynthesis(
                'Brc1c2ccccc2c(Br)c2ccccc12'
            )
        """
        if self.project_id is None:
            raise ValueError("Project identifier has to be set first.")
        payload = {"projectId": self.project_id, "aiModel": ai_model}
        data = {
            "aiModel": ai_model,
            "isinteractive": False,
            "parameters": {
                "availability_pricing_threshold": availability_pricing_threshold,
                "available_smiles": available_smiles,
                "exclude_smiles": exclude_smiles,
                "exclude_substructures": exclude_substructures,
                "exclude_target_molecule": exclude_target_molecule,
                "fap": fap,
                "max_steps": max_steps,
                "nbeams": nbeams,
                "pruning_steps": pruning_steps,
            },
            "product": product,
        }
        response = requests.post(
            self.routes.retrosynthesis_prediction_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
            params=payload,
        )
        return response

    @response_handling(
        success_status_code=200, on_success=automatic_retrosynthesis_results_on_success
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
            providing the prediction identifier:

            >>> rxn4chemistry_wrapper.get_predict_automatic_retrosynthesis_results(
                response['response']['payload']['id']
                # or response['prediction_id']
            )
            {...}
        """
        response = requests.get(
            self.routes.retrosynthesis_prediction_results_url.format(
                prediction_id=prediction_id
            ),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=retrosynthesis_sequence_pdf)
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
            sequence identifier:

            >>> rxn4chemistry_wrapper.get_retrosynthesis_sequence_pdf(
                response['response']['payload']['id'],
                '5e788ae548260b770105ecf4'
            )
            {...}
        """
        response = requests.get(
            self.routes.retrosynthesis_sequence_pdf_url.format(
                prediction_id=prediction_id, sequence_id=sequence_id
            ),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(
        success_status_code=200, on_success=paragraph_to_actions_on_success
    )
    @ibm_rxn_api_limits
    def paragraph_to_actions(self, paragraph: str) -> requests.models.Response:
        """
        Get the actions from a paragraph describing a recipe.

        Args:
            paragraph (str): paragraph describing a recipe.

        Returns:
            dict: dictionary containing the actions.

        Examples:
            Get actions from a paragraph:

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
        data = {"paragraph": paragraph}
        response = requests.post(
            self.routes.paragraph2actions_url,
            headers=self.headers,
            data=json.dumps(data).encode(),
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=synthesis_id_on_success)
    @ibm_rxn_api_limits
    def create_synthesis_from_sequence(
        self, sequence_id: str, ai_model: str = "2020-10-20"
    ) -> requests.models.Response:
        """
        Create a new synthesis from a sequence identifier.

        A sequence id can be retrieved from the results of an automated retrosynthesis
        prediction.

        Args:
            sequence_id (str): a sequence identifier returned by
                predict_automatic_retrosynthesis_results.
            ai_model (str, optional): model release. Defaults to
                '2020-10-20'.

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
            raise ValueError("Project identifier has to be set first.")
        data = {
            "sequenceId": sequence_id,
            "projectId": self.project_id,
            "aiModel": ai_model,
        }
        response = requests.post(
            self.routes.synthesis_creation_from_sequence_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=synthesis_on_success)
    @ibm_rxn_api_limits
    def get_synthesis_procedure(self, synthesis_id: str) -> requests.models.Response:
        """
        Get a synthesis procedure based on its identifier.

        The provided synthesis identifier can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the the response.

        Examples:
            Retrieve a synthesis procedure by providing the desired sequence identifier:

            >>> response = rxn4chemistry_wrapper.get_synthesis(
                '5dd273618sid4897af'
            )
        """
        response = requests.get(
            self.routes.synthesis_procedure_url.format(synthesis_id=synthesis_id),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=synthesis_on_success)
    @ibm_rxn_api_limits
    def get_synthesis_execution(self, synthesis_id: str) -> requests.models.Response:
        """
        Get a synthesis procedure based on its identifier.

        The provided synthesis identifier can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the the response.

        Examples:
            Retrieve a synthesis procedure by providing the desired sequence identifier:

            >>> response = rxn4chemistry_wrapper.get_synthesis(
                '5dd273618sid4897af'
            )
        """
        response = requests.get(
            self.routes.synthesis_execution_url.format(synthesis_id=synthesis_id),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(
        success_status_code=200, on_success=synthesis_execution_status_on_success
    )
    @ibm_rxn_api_limits
    def get_synthesis_status(self, synthesis_id: str) -> requests.models.Response:
        """
        Get the status of a given synthesis execution based on its identifier.

        The provided synthesis identifier can be obtained as a previous step
        by calling the create_synthesis_from_sequence() method.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.

        Returns:
            dict: dictionary containing the the response.

        Examples:
            Get a synthesis execution statu by providing the desired sequence identifier:

            >>> response = rxn4chemistry_wrapper.get_synthesis_status(
                '5dd273618sid4897af'
            )
        """
        response = requests.get(
            self.routes.synthesis_status_url.format(synthesis_id=synthesis_id),
            headers=self.headers,
            cookies={},
        )
        return response

    @response_handling(
        success_status_code=200, on_success=synthesis_execution_id_on_success
    )
    @ibm_rxn_api_limits
    def start_synthesis(self, synthesis_id: str) -> requests.models.Response:
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
            self.routes.synthesis_start_url.format(synthesis_id=synthesis_id),
            headers=self.headers,
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def get_node_ids(self, synthesis_id: str) -> List[str]:
        """
        Get a list of node ids

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.
        Returns:
            List: containing the node identifiers.

        Examples:
            Start the synthesis with a given identifier:

            >>> response = rxn4chemistry_wrapper.get_node_ids(
                synthesis_id='5dd273618sid4897af'
            )
        """

        response = self.get_synthesis_procedure(synthesis_id=synthesis_id)
        tree: Dict = copy.deepcopy(
            response["response"]["payload"]["sequences"][0]["tree"]
        )
        ordered_tree_nodes = post_order_tree_traversal(tree=tree)

        node_ids = [node["id"] for node in ordered_tree_nodes]

        return node_ids

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

            >>> result = rxn4chemistry_wrapper.get_synthesis_plan(
                synthesis_id='5dd273618sid4897af'
            )
        """
        raise DeprecationWarning(
            "Deprecated method use get_node_ids() to get the node ids and get_reaction_settings() to get the actions of a synthesis procedure!"
        )

    def get_synthesis_execution_plan(
        self, synthesis_id: str
    ) -> Tuple[Dict, List, List]:
        """
        Return the synthesis tree for the given synthesis_id for an execution.

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

            >>> result = rxn4chemistry_wrapper.get_synthesis_execution_plan(
                synthesis_id='5dd273618sid4897af'
            )
        """
        response = self.get_synthesis_execution(synthesis_id=synthesis_id)
        response = self.get_synthesis_procedure(
            synthesis_id=response["response"]["payload"]["content"][-1]["synthesisId"]
        )
        tree: Dict = copy.deepcopy(
            response["response"]["payload"]["sequences"][0]["tree"]
        )

        ordered_tree_nodes = post_order_tree_traversal(tree=tree)
        keys_to_keep = ["id", "smiles", "actions", "children"]
        flattened_actions = []

        for node in ordered_tree_nodes:
            [node.pop(key) for key in list(node.keys()) if key not in keys_to_keep]
            flattened_actions.extend(node["actions"])
        return tree, ordered_tree_nodes, flattened_actions

    def get_node_actions(self, synthesis_id: str, node_id: str) -> List[Dict]:
        """
        Return a list of dictionaries describing the actions for a specific node in
        a synthesis tree. All the automatically generated fields are filtered out
        and returns only the editable fields for each dictionary.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.
            node_id (str): the 'id' field of a specific node in the synthesis tree

        Returns:
            List[Dict]: List of dictionaries of all the actions in the specific
                node, simplified to only include editable fields.

        Examples:
            Return the list of actions for the given synthesis and node identifier:

            >>> result = rxn4chemistry_wrapper.get_node_actions(
                synthesis_id='5dd273618sid4897af', node_id='5z7f6bgz6g95gcbh'
            )
        """
        raise DeprecationWarning(
            "Deprecated method use get_node_ids() to get the node ids and get_reaction_settings() to get the actions of a synthesis procedure!"
        )

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def update_node_actions(
        self, synthesis_id: str, node_id: str, actions: List[Dict[str, Any]]
    ) -> requests.models.Response:
        """
        Update the list of actions for a specific node. The given actions will completely replace
        the existing actions for this node in the tree.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.
            node_id (str): the 'id' field of a specific node in the synthesis tree
            actions (List[Dict[str, Any]): A list of actions which will completely replace
                the existing actions for this node.

        Returns:
            dict: dictionary containing the .pdf report.
        Examples:
            Update the list of actions for the given synthesis and node identifier:

            >>> result = rxn4chemistry_wrapper.update_node_actions(
                    synthesis_id='5dd273618sid4897af',
                    node_id='5z7f6bgz6g95gcbh',
                    actions=[
                        {
                            'name': 'add',
                            "content": {
                                "atmosphere": None,
                                "duration": None,
                                "temperature": None,
                                "dropwise": {
                                  "value": False,
                                  "quantity": None,
                                  "unit": None
                                },
                                "material": {
                                  "value": "ethanol",
                                  "quantity": {
                                    "value": 10,
                                    "unit": "ml"
                                  },
                                  "unit": None
                                }
                            },
                        }
                    ]
                )
        """

        raise DeprecationWarning(
            "Deprecated method use get_node_ids() to get the node ids and get_reaction_settings() to get the actions of a synthesis procedure!"
        )

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def predict_reaction_properties(
        self,
        reactions: List[str],
        ai_model: str = "atom-mapping-2020",
    ) -> requests.models.Response:
        """
        Launch prediction with given reaction SMILES strings.

        Args:
            reactions: list of reaction smiles to predict reaction properties.
            ai_model: model flavour and release. "atom-mapping-2020" for the default
                atom mapping model, "yield-2020-08-10" for the default yield model.
        Returns:
            dict: dictionary containing the response.

        Examples:
            Predict reaction properties by providing the reaction SMILES and aiModel:

            >>> response = rxn4chemistry_wrapper.predict_reaction_properties_from_smiles(
            ...     reactions=["CCCCCCO>>CCCCCCCO"],
            ...     ai_model="atom-mapping-2020"
            ... )
        """
        data = {
            "aiModel": ai_model,
            "reactions": reactions,
        }
        response = requests.post(
            self.routes.reaction_properties_predictions_from_smiles_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def current_user(self) -> requests.models.Response:
        """
        Get user info of the current user API key

        Returns:
            dict: dictionary with current user info

        Examples:
            Getting infos of the current user.
            >>> response = rxn4chemistry_wrapper.current_user()
        """
        response = requests.get(
            self.routes.users_current_url, headers=self.headers, cookies={}
        )

        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def update_roborxn_api_key(
        self, user_id: str, roborxn_api_key: str
    ) -> requests.models.Response:
        """
        update the roboRxnApiKey for the user specified with it user_id
        Args:
            user_id (str): user_id
            roborxn_api_key (str): new API key to updated

        Returns:
            dict: dictionary containing the updated user information

        Examples:
            Updating the roboRxnApiKey of the user "test_user_id".
            >>> response = rxn4chemistry_wrapper.update_roborxn_api_key(
              user_id = 'test_user_id',
              roborxn_api_key = 'NEW-roborxn_api_key')
        """
        data = {
            "roboRxnApiKey": roborxn_api_key,
        }

        response = requests.patch(
            self.routes.users_id_url.format(user_id=user_id),
            data=json.dumps(data),
            headers=self.headers,
            cookies={},
        )

        return response

    @response_handling(success_status_code=200, on_success=reaction_settings_on_success)
    @ibm_rxn_api_limits
    def get_reaction_settings(
        self, synthesis_id: str, node_id: str
    ) -> requests.models.Response:
        """
        Retrieves a the actions and product from a specified synthesis and node.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.
            node_id (str): the 'id' field of a specific node in the synthesis tree

        Returns:
            actions (List[Dict[str, Any]): A list of actions which will completely replace
                the existing actions for this node.
            products (List[Dict[str, Any]): A list of product which will completely replace
                the existing product for this node.

        Examples:
            Getting the actions and product of a synthesis.
            >>> actions_and_product = rxn4chemistry_wrapper.get_reaction_settings(
                            synthesis_id='5dd273618sid4897af',
                            node_id='5z7f6bgz6g95gcbh')
        """

        response = requests.get(
            self.routes.synthesis_reaction_setting_url.format(
                synthesis_id=synthesis_id, node_id=node_id
            ),
            headers=self.headers,
            cookies={},
        )

        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def update_reaction_settings(
        self,
        synthesis_id: str,
        node_id: str,
        actions: List[Dict[str, Any]],
        product: Dict[str, Any],
    ) -> requests.models.Response:
        """
        Update the list of actions and products for a specific node.

        The given actions will completely replace the existing actions for this node in the tree.
        The given products will completely replace the existing product for this node in the tree.

        Args:
            synthesis_id (str): a synthesis identifier returned by
                create_synthesis_from_sequence() method.
            node_id (str): the 'id' field of a specific node in the synthesis tree
            actions (List[Dict[str, Any]): A list of actions which will completely replace
                the existing actions for this node.
            product (Dict[str, Any]): A list of product which will completely replace
                the existing product for this node.

        Returns:
            dict: dictionary containing the response.
        Examples:
            Update the list of actions and product for the given synthesis and node identifier:

            >>> result = rxn4chemistry_wrapper.update_reaction_settings(
                    synthesis_id='5dd273618sid4897af',
                    node_id='5z7f6bgz6g95gcbh',
                    actions=[
                        {
                            'name': 'add',
                            "content": {
                                "atmosphere": None,
                                "duration": None,
                                "temperature": None,
                                "dropwise": {
                                  "value": False,
                                  "quantity": None,
                                  "unit": None
                                },
                                "material": {
                                  "value": "ethanol",
                                  "quantity": {
                                    "value": 10,
                                    "unit": "ml"
                                  },
                                  "unit": None
                                }
                            },
                        }
                    ],
                product={"product":{
                                "moleculeInfo":{
                                "density": 997,
                                "molecularWeight":214,
                                "name": "N-(4-bromophenyl)acetamide"},
                                "productMassAndReactionInformation":{
                                        "unit": "mg",
                                        "quantity": 500,
                                        "securityFactor": 1.1,
                                        "stoichiometryFactor": 1.0,
                                        "yield": 0.9
                             }
                        }
                )
        """
        response = requests.put(
            self.routes.synthesis_reaction_setting_url.format(
                synthesis_id=synthesis_id, node_id=node_id
            ),
            headers=self.headers,
            data=json.dumps({"actions": actions, "product": product}),
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def batch_executor_download_from_uri(
        self,
        s3_path: str,
    ) -> requests.models.Response:
        """
        Creates a presigned URI for downloading a file in S3.

        Args:
            s3_path: a s3 uri.

        Returns:
            A presigned URI for download.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run an example using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_download_from_uri(s3_path="mock/dummy_input.jsonl")
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        params = {"s3_path": s3_path}
        response = requests.get(
            self.routes.batch_executor_download_from_uri_url,
            headers=self.headers,
            params=params,
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def batch_executor_read_from_uri(
        self,
        s3_path: str,
    ) -> requests.models.Response:
        """
        Read the content of an input/output file in S3.

        Args:
            s3_path: a s3 uri.

        Returns:
            The list of lines in the file.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run an example using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_read_from_uri(s3_path="mock/dummy_input.jsonl")
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        params = {"s3_path": s3_path}
        response = requests.get(
            self.routes.batch_executor_read_from_uri_url,
            headers=self.headers,
            params=params,
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def batch_executor_job_id_to_status(
        self,
        job_id_list: List[str],
    ) -> requests.models.Response:
        """
        Get the status of a list of submitted Ray jobs.

        Args:
            job_id_list: the list of submitted Ray jobs.

        Returns:
            The status of the list of submitted Ray jobs.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run an example using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_job_id_to_status({"job_id_list": [""]})
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        params = {"job_id_list": job_id_list}
        response = requests.get(
            self.routes.batch_executor_job_id_to_status_url,
            headers=self.headers,
            params=params,
            cookies={},
        )
        return response

    @response_handling(success_status_code=200, on_success=default_on_success)
    @ibm_rxn_api_limits
    def batch_executor_predict_from_request_via_job(
        self,
        inputs: List[Dict[str, List[str]]],
        batch_size: int,
        topn: int,
        task: str,
        model_type: str,
        model_tag: str,
        s3_batch_folder: str = "batches/",
        s3_pred_folder: str = "batches_predictions/",
        delete_temporary_s3_files: bool = True,
    ) -> requests.models.Response:
        """
        Run a batch prediction from reactions specified directly in
            the request body using Ray's JobSubmissionClient.

        Args:
            inputs: List with precursors and products.
            batch_size: Limits number of elements per batch.
            topn: Defines topn.
            task: Identifies the task.
            model_type: Defines the model type.
            model_tag: Specifies the tag of the model.
            s3_batch_folder: Defines a folder on s3 for the batch.
            s3_pred_folder: Defines a folder on s3 for the prediction.
            delete_temporary_s3_files: Boolean to delete temporary s3 files.

        Returns:
            The predictions and optionally the path of the output file in S3
            where they are stored.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run a batch prediction using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_predict_from_request_via_job(
                {
                    "batch_size": 10,
                    "topn": 5,
                    "task": "",
                    "model_type": "",
                    "model_tag": "",
                    "s3_batch_folder": "batches/",
                    "s3_pred_folder": "batches_predictions/",
                    "content": {
                        inputs=[
                            {
                                precursors: [],
                                products: []
                            }
                        ],
                        delete_temporary_s3_files=True
                    }
                }
            )
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        data = {
            "batch_size": batch_size,
            "topn": topn,
            "task": task,
            "model_type": model_type,
            "model_tag": model_tag,
            "s3_batch_folder": s3_batch_folder,
            "s3_pred_folder": s3_pred_folder,
            "content": {
                "inputs": inputs,
                "delete_temporary_s3_files": delete_temporary_s3_files,
            },
        }
        response = requests.post(
            self.routes.batch_executor_predict_from_request_via_job_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def batch_executor_predict_from_uri_via_job(
        self,
        input_s3_path: str,
        output_s3_path: str,
        batch_size: int,
        topn: int,
        task: str,
        model_type: str,
        model_tag: str,
        s3_batch_folder: str = "batches/",
        s3_pred_folder: str = "batches_predictions/",
    ) -> requests.models.Response:
        """
        Run a batch prediction from a file in s3 using Ray's JobSubmissionClient.

        Args:
            input_s3_path: S3 path for input file.
            output_s3_path: S3 path for output file.
            batch_size: Limits number of elements per batch.
            topn: Defines topn.
            task: Identifies the task.
            model_type: Defines the model type.
            model_tag: Specifies the tag of the model.
            s3_batch_folder: Defines a folder on s3 for the batch.
            s3_pred_folder: Defines a folder on s3 for the prediction.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run a batch prediction using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_predict_from_uri_via_job(
                {
                    "batch_size": 10,
                    "topn": 5,
                    "task": "",
                    "model_type": "",
                    "model_tag": "",
                    "s3_batch_folder": "batches/",
                    "s3_pred_folder": "batches_predictions/",
                    "content": {
                        "input_s3_path": "",
                        "output_s3_path": ""
                    }
                }
            )
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        data = {
            "batch_size": batch_size,
            "topn": topn,
            "task": task,
            "model_type": model_type,
            "model_tag": model_tag,
            "s3_batch_folder": s3_batch_folder,
            "s3_pred_folder": s3_pred_folder,
            "content": {
                "input_s3_path": input_s3_path,
                "output_s3_path": output_s3_path,
            },
        }
        response = requests.post(
            self.routes.batch_executor_predict_from_uri_via_job_url,
            headers=self.headers,
            data=json.dumps(data),
            cookies={},
        )
        return response

    @ibm_rxn_api_limits
    def batch_executor_job_id_to_time(
        self,
        job_id_list: List[str],
    ) -> requests.models.Response:
        """
        Get the run times of a list completed Ray jobs.

        Args:
            job_id_list: the list of submitted Ray jobs.

        Returns:
            The run times of the list of submitted Ray jobs.

        Raises:
            ValueError: in case the batch executor url is not set.

        Examples:
            Run an example using the wrapper:

            >>> rxn4chemistry_wrapper.batch_executor_job_id_to_time({"job_id_list": [""]})
        """
        if self.routes.batch_executor_base_url is None:
            raise ValueError("Batch executor endpoints are not configured correctly.")

        params = {"job_id_list": job_id_list}
        response = requests.get(
            self.routes.batch_executor_job_id_to_time_url,
            headers=self.headers,
            params=params,
            cookies={},
        )
        return response
