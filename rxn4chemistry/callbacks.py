"""Callbacks for IBM RXN for Chemistry API."""
import logging
import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger('rxn4chemistry:callbacks')

BORDER_COLOR_COMMERCIAL = "#28a30d"
BORDER_COLOR_UNAVAILABLE = "#ce4e04"


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
    return {
        'prediction_id': response_dict['payload']['id'],
        'response': response_dict
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
    return {
        'synthesis_id': response_dict['payload']['id'],
        'response': response_dict
    }


def default_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {'response': response_dict}


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

    # process children recursively
    if 'children' in tree:
        tree['children'] = [_postprocess_retrosynthesis_tree(child) for child in tree['children']]

    try:
        tree['isCommercial'] = tree['metaData']['borderColor'] == BORDER_COLOR_COMMERCIAL
    except KeyError:
        pass

    return tree


def automatic_retrosynthesis_results_on_success(
    response: requests.models.Response
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
        'retrosynthetic_paths':
            [
                _postprocess_retrosynthesis_tree(sequence['tree'])
                for sequence in response_dict['payload']['sequences']
            ],
        'status': response_dict['payload']['status'],
        'response': response_dict
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
    return {'content': response.text}


def synthesis_analysis_report_pdf(response: requests.models.Response) -> dict:
    """
    Process the successful response of .pdf spectrometer report
    retrieval.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    return {'content': response.text}


def paragraph_to_actions_on_success(
    response: requests.models.Response
) -> dict:
    """
    Process the successful response of a paragraph to actions request.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {
        'actions': [
            action.strip(' .')
            for element in BeautifulSoup(
                response_dict['payload']['actionSequence'],
                'html.parser'
            ).find_all('li')
            for action in element.text.split(';')
        ],
        'response': response_dict
    }


def synthesis_status_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of requests returning a synthesis
    identifier.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    response_dict['payload'].pop('user')

    return {
        'status': response_dict['payload']['status'],
        'response': response_dict
    }
