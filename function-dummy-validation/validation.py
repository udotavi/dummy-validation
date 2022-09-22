"""
main init file
"""

import logging
import json
import requests
import azure.functions as func
from azure.identity import DefaultAzureCredential


def main(msg: func.ServiceBusMessage):
    """
    This is the main function
    """

    logging.info("hello world")
    # logging.info(msg.get_body())

    uri = "https://graph.microsoft.com/v1.0/users"

    logging.info(graph_response(uri))


def graph_response(uri: str):
    """
    Returns:
        graph_response_dict (dict): Response body in a dictionary format
    """
    scope = "https://graph.microsoft.com/.default"

    access_token = DefaultAzureCredential().get_token(scope).token
    headers = {"Authorization": "Bearer " + access_token}

    api_response = requests.get(uri, headers=headers)

    graph_response_dict = json.loads(api_response.content)

    return graph_response_dict
