"""Callbacks for IBM RXN for Chemistry API."""
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

BORDER_COLOR_COMMERCIAL = set(["#28a30d", "#0f62fe", "#002d9c"])
BORDER_COLOR_UNAVAILABLE = set(["#ce4e04"])
MODEL_NAMES_MAPPING = {
    "PARAGRAPH2ACTIONS": "paragraph-to-actions",
    "SMILES2ACTIONS": "sequence-to-actions",
    "REACTION": "reaction-prediction-model",
    "RETROSYNTHESIS": "retrosynthesis-prediction-model",
}
MODEL_FIELDS_MAPPING = {"name": "name"}


def prediction_id_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a prediction
    identifier.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {"prediction_id": response_dict["payload"]["id"], "response": response_dict}


def task_id_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a task identifier.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {
        "task_id": response_dict["payload"]["task_id"],
        "task_status": response_dict["payload"]["task_status"],
    }


def synthesis_id_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a synthesis
    identifier.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {"synthesis_id": response_dict["payload"]["id"], "response": response_dict}


def default_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {"response": response_dict}


def _postprocess_retrosynthesis_tree(tree: dict) -> dict:
    """
    Postprocess retrosynthesis tree.

    Postprocessing actions:
    * Correct `isCommercial` field based on metaData/borderColor.

    Args:
        tree (dict): Retrosynthesis tree

    Returns:
        dict: postprocessed retrosynthesis tree
    """

    children = tree.get("children", [])
    # node is a leaf
    if len(children) == 0:
        try:
            tree["isCommercial"] = (
                tree["metaData"]["borderColor"] in BORDER_COLOR_COMMERCIAL
            )
        except KeyError:
            logger.warning("no information on commercial availability")
            pass
    else:
        # process children recursively
        tree["children"] = [
            _postprocess_retrosynthesis_tree(child) for child in tree["children"]
        ]

    return tree


def automatic_retrosynthesis_results_on_success(
    response: requests.models.Response,
) -> dict:
    """
    Process the successful response of an automatic retrosyntesis result
    request.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()

    return {
        "retrosynthetic_paths": [
            _postprocess_retrosynthesis_tree(sequence["tree"])
            for sequence in response_dict["payload"]["sequences"]
        ],
        "status": response_dict["payload"]["status"],
        "response": response_dict,
    }


def retrosynthesis_sequence_pdf(response: requests.models.Response) -> dict:
    """
    Process the successful response of .pdf retrosynthesis sequence report
    retrieval.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    return {"content": response.text}


def synthesis_analysis_report_pdf(response: requests.models.Response) -> dict:
    """
    Process the successful response of .pdf spectrometer report
    retrieval.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    return {"content": response.text}


def paragraph_to_actions_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of a paragraph to actions request.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {
        "actions": [
            action.strip(" .")
            for element in BeautifulSoup(
                response_dict["payload"]["actionSequence"], "html.parser"
            ).find_all("li")
            for action in element.text.split(";")
        ],
        "response": response_dict,
    }


def synthesis_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a synthesis procedure.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    response_dict["payload"].pop("user", None)

    return {"response": response_dict}


def synthesis_execution_status_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a synthesis execution status.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    response_dict["payload"].pop("user", None)

    return {"status": response_dict["payload"]["status"], "response": response_dict}


def synthesis_execution_id_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a synthesis execution identifier.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    response_dict["payload"].pop("user", None)

    return {
        "synthesis_execution_id": response_dict["payload"]["id"],
        "response": response_dict,
    }


def predict_reaction_batch_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning predict reaction batch results.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    identifier = response_dict["payload"]["task"]["task_id"]
    status = response_dict["payload"]["task"]["status"]
    return_dict = {}
    if status == "DONE":
        return response_dict["payload"]["result"]
    elif status == "WAITING":
        return_dict[
            "message"
        ] = "Task waiting: either the task is submitted and not running or it does not exists in the queue."
    return_dict["task_id"] = identifier
    return_dict["task_status"] = status
    return return_dict


def model_listing_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a supported model list.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    models = response_dict["payload"]["models"]
    return {
        MODEL_NAMES_MAPPING[model_type]: [
            {
                MODEL_FIELDS_MAPPING[model_field]: model_value
                for model_field, model_value in model_info.items()
                if model_field in MODEL_FIELDS_MAPPING
            }
            for model_info in model_list
        ]
        for model_type, model_list in models.items()
        if model_type in MODEL_NAMES_MAPPING
    }
