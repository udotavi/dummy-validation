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
    logging.info(msg.get_body())

    for group in ["Developers", "Admin"]:
        print(f"   ### checking for {group}..")

        # Automation Scope Check..
        if not group_in_au(group, "Automation AU"):
            logging.info("Group - %s is not under automation scope yet", group)



def request_graph(uri: str, custom_headers: dict = None) -> dict:
    """
    Returns:
        graph_response_dict (dict): Response body in a dictionary format
    """
    scope = "https://graph.microsoft.com/.default"

    access_token = DefaultAzureCredential().get_token(scope).token
    headers = dict(
        {"Authorization": "Bearer " + access_token},
        **custom_headers if custom_headers else {}
    )

    api_response = requests.get(uri, headers=headers, timeout=3000)

    graph_response_dict = json.loads(api_response.content)

    return graph_response_dict

def group_in_au(group_name: str, au_name: str) -> bool:
    """
    AU check
    """

    graph_api_version = "https://graph.microsoft.com/v1.0"

    group_id_endpoint = (
        f"{graph_api_version}/groups?$select=id&$filter=displayName eq '{group_name}'"
    )

    # {
    # "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#groups(id)",
    # "value": [
    #     {
    #         "id": "02bd9fd6-8f93-4758-87c3-1fb73740a315"
    #     }
    # ]
    # }

    group_id = request_graph(group_id_endpoint)["value"][0][
        "id"
    ]  # gets group id from returned dict

    au_membership_endpoint = f"{graph_api_version}/groups/{group_id}/memberOf/microsoft.graph.administrativeUnit?$select=displayName&$count=true&$filter=displayName eq '{au_name}'"

    # {
    #     "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects/microsoft.graph.administrativeUnit(displayName)",
    #     "@odata.count": 0,
    #     "value": [
    #         {
    #             "displayName": "Security AU"
    #         }
    #     ]
    # }

    au_list = request_graph(au_membership_endpoint, {"ConsistencyLevel": "eventual"})[
        "value"
    ]  # check if au is in the list

    is_member = bool(au_list)

    logging.info("Membership Status: %s", is_member)

    return is_member
