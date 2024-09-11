"""
Entra ID Sign-In Logs Retrieval Module

This module retrieves and saves Entra ID sign-in logs using Microsoft Graph API.

Functions:
- get_access_token(): Authenticates using AzureCliCredential to get an access token.
- get_sign_in_logs(): Retrieves sign-in logs from Microsoft Graph API.
- save_sign_in_logs(): Saves the retrieved sign-in logs to a JSON file.
"""

import requests
import json
from azure.identity import AzureCliCredential
from datetime import datetime

def get_access_token(resource="https://graph.microsoft.com/.default", credential=None):
    """
    Authenticate using AzureCliCredential to get an access token.

    Parameters:
    - resource: The resource URL for which the token is requested.
    - credential: Optional Azure credential to use for authentication.

    Returns:
    The access token.
    """
    if credential is None:
        credential = AzureCliCredential()
    token = credential.get_token(resource)
    return token.token

def get_sign_in_logs(start_time: datetime, end_time: datetime, credential=None):
    """
    Retrieve sign-in logs from Microsoft Graph API within a specified time range.

    Parameters:
    - start_time: The start time for the sign-in logs.
    - end_time: The end time for the sign-in logs.
    - credential: Optional Azure credential to use for authentication.

    Returns:
    The sign-in logs data.
    """
    start_time_str = start_time.isoformat(timespec='milliseconds') + 'Z'
    end_time_str = end_time.isoformat(timespec='milliseconds') + 'Z'
    url = f'https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=createdDateTime ge {start_time_str} and createdDateTime le {end_time_str}'
    token = get_access_token(resource="https://graph.microsoft.com/.default", credential=credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve sign-in logs. Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return None

def save_sign_in_logs(logs, filename):
    """
    Saves the retrieved sign-in logs to a JSON file.

    Parameters:
    - logs: The list of sign-in log entries.
    - filename: The name of the file to save logs to.
    """
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=4)
    print(f"Sign-in logs saved to: {filename}")

def main(start_time: datetime, end_time: datetime, credential=None):
    """
    Main function to retrieve and save sign-in logs within a specified time range.

    Parameters:
    - start_time: The start time for the sign-in logs.
    - end_time: The end time for the sign-in logs.
    - credential: Optional Azure credential to use for authentication.
    """
    sign_in_logs = get_sign_in_logs(start_time, end_time, credential=credential)
    if sign_in_logs:
        return sign_in_logs
    return []