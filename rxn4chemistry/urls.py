"""URL routes for IBM RXN for Chemistry API."""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
from typing import Optional


class RXN4ChemistryRoutes:
    """
    Routes for RXN for Chemistry service.
    """

    def __init__(self, base_url: Optional[str] = None, api_version: str = "v1") -> None:
        """
        Initialize the routes.

        Args:
            base_url (str, optional): base url for the service. If not provided it will default to
                the environment variable RXN4CHEMISTRY_BASE_URL or https://rxn.res.ibm.com.
            api_version (str, optional): api version. If not provided it will default to
                v1.
        """
        self._base_url = (
            base_url
            if base_url
            else os.getenv("RXN4CHEMISTRY_BASE_URL", "https://rxn.res.ibm.com")
        )
        self._api_version = api_version
        self._update_routes()

    def _update_routes(self) -> None:
        """Update all the routes."""
        self.api_url = "{}/{}".format(
            self._base_url, f"rxn/api/api/{self._api_version}"
        )
        self.models_url = "{}/{}".format(self.api_url, "ai-models")
        self.project_url = "{}/{}".format(self.api_url, "projects")
        self.predictions_url = "{}/{}".format(self.api_url, "predictions")
        self.users_url = "{}/{}".format(self.api_url, "users")
        self.all_models_url = "{}/{}".format(self.models_url, "all")
        self.project_models_url = self.models_url
        self.attempts_url = "{}/{}/{}".format(
            self.project_url, "{project_id}", "attempts"
        )
        self.retro_attempts_url = "{}/{}/{}".format(
            self.project_url, "{project_id}", "retrosynthesis-attempt"
        )
        self.retrosynthesis_url = "{}/{}".format(self.api_url, "retrosynthesis")
        self.reaction_prediction_url = "{}/{}".format(self.predictions_url, "pr")
        self.reaction_prediction_results_url = "{}/{}".format(
            self.predictions_url, "{prediction_id}"
        )
        self.reaction_prediction_batch_url = "{}/batch".format(
            self.reaction_prediction_url, "batch"
        )
        self.reaction_prediction_batch_results_url = "{}/{}".format(
            self.reaction_prediction_batch_url, "{task_id}"
        )
        self.retrosynthesis_prediction_url = "{}/{}".format(
            self.retrosynthesis_url, "rs"
        )
        self.retrosynthesis_prediction_results_url = "{}/{}".format(
            self.retrosynthesis_url, "{prediction_id}"
        )
        self.retrosynthesis_sequence_pdf_url = "{}/sequences/{}/download-pdf".format(
            self.retrosynthesis_prediction_results_url, "{sequence_id}"
        )
        self.paragraph2actions_url = "{}/{}".format(self.api_url, "paragraph-actions")
        self.synthesis_url = "{}/{}".format(self.api_url, "synthesis")
        self.synthesis_procedure_url = "{}/{}".format(
            self.synthesis_url, "{synthesis_id}"
        )
        self.synthesis_creation_from_sequence_url = "{}/{}".format(
            self.synthesis_url, "create-from-sequence"
        )
        self.synthesis_patch_node_actions_url = "{}/{}/{}/{}".format(
            self.synthesis_url, "{synthesis_id}", "node", "{node_id}"
        )
        self.synthesis_execution_url = "{}/{}".format(
            self.api_url, "synthesis-executions"
        )
        self.synthesis_status_url = "{}/{}".format(
            self.synthesis_execution_url, "{synthesis_id}"
        )
        self.synthesis_start_url = "{}/{}/{}".format(
            self.synthesis_execution_url, "{synthesis_id}", "start"
        )

        self.users_id_url = "{}/{}".format(self.users_url, "{user_id}")
        self.users_current_url = "{}/{}".format(self.users_url, "current")

    @property
    def base_url(self) -> str:
        """
        Get the base url for the RXN for Chemistry service.

        Returns:
            str: base url for the service.
        """
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        """
        Set the base url for the RXN for Chemistry service.

        Args:
            value (str): bease url to set.
        """
        self._base_url = value
        self._update_routes()
