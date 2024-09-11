"""
Azure Audit Logs Retrieval Module

This module retrieves and normalizes Azure audit logs for all subscriptions.
It uses the Azure SDK for authentication and to retrieve the subscriptions.
The module collects audit logs within a specified time range.

Functions:
- get_access_token(): Authenticates using AzureCliCredential to get an access token.
- list_subscriptions(): Lists all Azure subscriptions.
- collect_audit_logs(): Collects audit logs for a specific subscription.
- save_audit_logs(): Saves the retrieved audit logs to a JSON file.
"""

import requests
from azure.identity import AzureCliCredential
import json

def get_access_token(credential=None):
    """
    Authenticate using AzureCliCredential to get an access token.

    Returns:
    The access token.
    """
    if credential is None:
        credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default")
    return token.token

def list_subscriptions(headers):
    """
    List all Azure subscriptions.

    Parameters:
    - headers: The headers to include in the API request.

    Returns:
    List of subscriptions if the request is successful, otherwise an empty list.
    """
    subscriptions_url = "https://management.azure.com/subscriptions?api-version=2020-01-01"
    subscriptions_response = requests.get(subscriptions_url, headers=headers)

    if subscriptions_response.status_code == 200:
        return subscriptions_response.json()["value"]
    else:
        print(f"Failed to retrieve subscriptions. Status code: {subscriptions_response.status_code}")
        print(f"Error message: {subscriptions_response.text}")
        return []

def collect_audit_logs(subscription_id, headers, start_time, end_time):
    """
    Collect audit logs for a specific subscription.

    Parameters:
    - subscription_id: The ID of the subscription.
    - headers: The headers to include in the API request.
    - start_time: The start time for the audit logs.
    - end_time: The end time for the audit logs.

    Returns:
    List of collected audit logs for the subscription.
    """
    base_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Insights/eventtypes/management/values"
    params = {
        "api-version": "2015-04-01",
        "$filter": f"eventTimestamp ge '{start_time}' and eventTimestamp le '{end_time}'"
    }
    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Failed to retrieve audit logs for subscription {subscription_id}. Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return []

def save_audit_logs(logs, filename):
    """
    Saves the retrieved audit logs to a JSON file.

    Parameters:
    - logs: The list of audit log entries.
    - filename: The name of the file to save logs to.
    """
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=4)
    print(f"Combined audit logs saved to: {filename}")

def main(start_time, end_time, credential=None):
    """
    Main function to orchestrate the process of retrieving and saving audit logs for specified Azure subscriptions.

    Parameters:
    - start_time: The start time for the audit logs.
    - end_time: The end time for the audit logs.
    - credential: Optional Azure credential to use for authentication.
    """
    token = get_access_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Get the list of subscriptions
    subscriptions = list_subscriptions(headers)

    all_audit_logs = []

    # Loop through all subscriptions and collect audit logs
    for subscription in subscriptions:
        subscription_id = subscription["subscriptionId"]
        print(f"Collecting audit logs for subscription: {subscription_id}")
        audit_logs = collect_audit_logs(subscription_id, headers, start_time, end_time)
        all_audit_logs.extend(audit_logs)

    return all_audit_logs