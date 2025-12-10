"""URL routes for IBM RXN for Chemistry API."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from typing import Optional


class RXN4ChemistryRoutes:
    """
    Routes for RXN for Chemistry service.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        batch_executor_base_url: Optional[str] = None,
        api_version: str = "v1",
    ) -> None:
        """
        Initialize the routes.

        Args:
            base_url (str, optional): base url for the service. If not provided it will default to
                the environment variable RXN4CHEMISTRY_BASE_URL or https://rxn.res.ibm.com.
            batch_executor_base_url (str, optional): base url for the batch executor service. If not provided
                it will default to the environment variable BATCH_EXECUTOR_BASE_URL.
            api_version (str, optional): api version. If not provided it will default to
                v1.
        """
        self._base_url = (
            base_url
            if base_url
            else os.getenv(
                "RXN4CHEMISTRY_BASE_URL", "https://rxn.app.accelerate.science"
            )
        )
        self._batch_executor_base_url = (
            batch_executor_base_url
            if batch_executor_base_url
            else os.getenv("BATCH_EXECUTOR_BASE_URL")
        )
        self._api_version = api_version
        self._update_routes()

    def _update_routes(self) -> None:
        """Update all the routes."""
        self.api_url = "{}/{}".format(
            self._base_url, f"rxn/api/api/{self._api_version}"
        )
        # model urls
        self.models_url = "{}/{}".format(self.api_url, "ai-models")
        self.models_by_scope_url = "{}/{}".format(self.models_url, "{scope}")
        self.models_categories_by_scope_url = "{}/{}".format(
            self.models_by_scope_url, "categories"
        )
        self.all_models_url = "{}/{}".format(self.models_url, "all")

        # reaction properties prediction urls
        self.reaction_properties_predictions_url = "{}/{}".format(
            self.api_url, "reaction-properties-predictions"
        )
        self.reaction_properties_predictions_from_smiles_url = "{}/{}".format(
            self.reaction_properties_predictions_url, "from-smiles"
        )
        self.reaction_properties_predictions_from_file_url = "{}/{}".format(
            self.reaction_properties_predictions_url, "from-file"
        )

        # atom mapping urls
        self.atom_mapping_url = "{}/{}".format(self.api_url, "atom-mapping")
        self.atom_mapping_from_smiles_url = "{}/{}".format(
            self.atom_mapping_url, "from-smiles"
        )
        self.atom_mapping_from_file_url = "{}/{}".format(
            self.atom_mapping_url, "from-file"
        )

        # yield urls
        self.yield_url = "{}/{}".format(self.api_url, "yield")
        self.yield_from_smiles_url = "{}/{}".format(self.yield_url, "from-smiles")
        self.yield_from_file_url = "{}/{}".format(self.yield_url, "from-file")

        # fingerprint urls
        self.fingerprint_url = "{}/{}".format(self.api_url, "fingerprint")
        self.fingerprint_from_smiles_url = "{}/{}".format(
            self.fingerprint_url, "from-smiles"
        )
        self.fingerprint_from_file_url = "{}/{}".format(
            self.fingerprint_url, "from-file"
        )

        # file entry urls
        self.file_upload_url = "{}/{}".format(self.api_url, "file-entries/upload")

        # optical chemical recognition urls
        self.optical_chemical_recognition_url = "{}/{}".format(
            self.api_url, "optical-chemical-recognition"
        )

        # projects urls
        self.project_url = "{}/{}".format(self.api_url, "projects")
        self.attempts_url = "{}/{}/{}".format(
            self.project_url, "{project_id}", "attempts"
        )
        self.retro_attempts_url = "{}/{}/{}".format(
            self.project_url, "{project_id}", "retrosynthesis"
        )
        self.reaction_completion_url = "{}/{}/{}".format(
            self.project_url, "{project_id}", "reaction-completion-predictions"
        )
        self.reaction_completion_result_url = "{}/{}".format(
            self.reaction_completion_url.format(project_id="{project_id}"),
            "{prediction_id}",
        )

        # prediction (forward) urls
        self.predictions_url = "{}/{}".format(self.api_url, "predictions")
        self.reaction_prediction_url = "{}/{}".format(self.predictions_url, "pr")
        self.reaction_prediction_results_url = "{}/{}".format(
            self.predictions_url.format("{project_id}"), "{prediction_id}"
        )
        self.reaction_prediction_alternative_results_url = "{}/{}".format(
            self.predictions_url, "prb"
        )
        self.reaction_prediction_batch_url = "{}/{}".format(
            self.reaction_prediction_url, "batch"
        )
        self.reaction_prediction_batch_results_url = "{}/{}".format(
            self.reaction_prediction_batch_url, "{task_id}"
        )
        self.reaction_prediction_batch_topn_url = "{}/{}".format(
            self.reaction_prediction_url, "batch_topn"
        )
        self.reaction_prediction_batch_topn_results_url = "{}/{}".format(
            self.reaction_prediction_batch_topn_url, "{task_id}"
        )

        # retrosynthesis urls
        self.retrosynthesis_url = "{}/{}".format(self.api_url, "retrosynthesis")
        self.retrosynthesis_prediction_url = "{}/{}".format(
            self.retrosynthesis_url, "rs"
        )
        self.retrosynthesis_prediction_results_url = "{}/{}".format(
            self.retrosynthesis_url, "{prediction_id}"
        )
        self.retrosynthesis_sequence_pdf_url = "{}/sequences/{}/download-pdf".format(
            self.retrosynthesis_prediction_results_url, "{sequence_id}"
        )

        # paragraph2actions url
        self.paragraph2actions_url = "{}/{}".format(self.api_url, "paragraph-actions")

        # synthesis urls
        self.synthesis_url = "{}/{}".format(self.api_url, "synthesis")
        self.synthesis_reaction_setting_url = "{}/{}/{}/{}/{}".format(
            self.synthesis_url,
            "{synthesis_id}",
            "node",
            "{node_id}",
            "reaction-settings",
        )
        self.synthesis_procedure_url = "{}/{}".format(
            self.synthesis_url, "{synthesis_id}"
        )
        self.synthesis_creation_from_sequence_url = "{}/{}".format(
            self.synthesis_url, "create-from-sequence"
        )
        self.synthesis_patch_node_actions_url = "{}/{}/{}/{}".format(
            self.synthesis_url, "{synthesis_id}", "node", "{node_id}"
        )

        # synthesis execution urls
        self.synthesis_execution_url = "{}/{}".format(
            self.api_url, "synthesis-executions"
        )
        self.synthesis_status_url = "{}/{}".format(
            self.synthesis_execution_url, "{synthesis_id}"
        )
        self.synthesis_start_url = "{}/{}/{}".format(
            self.synthesis_execution_url, "{synthesis_id}", "start"
        )

        # user urls
        self.users_url = "{}/{}".format(self.api_url, "users")
        self.users_id_url = "{}/{}".format(self.users_url, "{user_id}")
        self.users_current_url = "{}/{}".format(self.users_url, "current")

        # batch executor urls
        self.batch_executor_download_from_uri_url = "{}/{}".format(
            self._batch_executor_base_url, "download-from-uri"
        )
        self.batch_executor_read_from_uri_url = "{}/{}".format(
            self._batch_executor_base_url, "read-from-uri"
        )
        self.batch_executor_job_id_to_status_url = "{}/{}".format(
            self._batch_executor_base_url, "list-jobs-status"
        )
        self.batch_executor_predict_from_request_via_job_url = "{}/{}".format(
            self._batch_executor_base_url, "predict-from-request"
        )
        self.batch_executor_predict_from_uri_via_job_url = "{}/{}".format(
            self._batch_executor_base_url, "predict-from-uri"
        )
        self.batch_executor_job_id_to_time_url = "{}/{}".format(
            self._batch_executor_base_url, "list-jobs-time"
        )

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

    @property
    def batch_executor_base_url(self) -> str:
        """
        Get the base url for the RXN for Chemistry service.

        Returns:
            str: base url for the service.
        """
        return self._batch_executor_base_url

    @batch_executor_base_url.setter
    def batch_executor_base_url(self, value: str) -> None:
        """
        Set the base url for the RXN for Chemistry service.

        Args:
            value (str): bease url to set.
        """
        self._batch_executor_base_url = value
        self._update_routes()
