"""Callbacks for IBM RXN for Chemistry API."""
import logging
import requests

LOGGER = logging.getLogger('rxn4chemistry:callbacks')


def prediction_id_on_success(response: requests.models.Response) -> dict:
    """
    Process the successful response of predict_reaction and 
    predict_automatic_retrosynthesis.

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


def automatic_retrosynthesis_results_on_success(
    response: requests.models.Response
) -> dict:
    """
    Process the successful response of get_predict_automatic_retrosynthesis_results.

    Args:
        response (requests.models.Response): response from an API request.

    Returns:
        dict: dictionary representing the response.
    """
    response_dict = response.json()
    return {
        'retrosynthetic_paths':
            [
                sequence['tree']
                for sequence in response_dict['payload']['sequences']
            ],
        'status': response_dict['payload']['status'],
        'response': response_dict
    }
