"""
GCP Organization-wide Audit Log Export Module (SDK-based)

This module retrieves and saves audit logs for an entire Google Cloud Platform (GCP) organization.
It uses the Google Cloud SDK for authentication and to retrieve the organization ID.
The module collects audit logs within a specified time range.

Functions:
- enable_api(): Enables the Cloud Resource Manager API for the project.
- get_organization_id(): Retrieves the organization ID using the Resource Manager API.
- get_audit_logs(): Retrieves and saves audit logs for the entire organization.
- save_audit_logs(): Saves the retrieved audit logs to a JSON file.
"""

import google.cloud.logging
from google.cloud import service_usage_v1
from google.cloud import resourcemanager_v3
from google.cloud.logging import DESCENDING
from google.auth import default
from datetime import datetime, timedelta
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load default credentials and project ID
credentials, project_id = default()

def enable_api(project_id: str, api_name: str):
    """
    Enables the specified API for the given project if it is not already enabled.
    
    Args:
        project_id (str): The project ID.
        api_name (str): The name of the API to enable.
    """
    client = service_usage_v1.ServiceUsageClient(credentials=credentials)
    
    # Check if the API is already enabled
    request = service_usage_v1.GetServiceRequest(
        name=f'projects/{project_id}/services/{api_name}'
    )
    response = client.get_service(request)
    
    if response.state == service_usage_v1.types.State.ENABLED:
        logging.info(f"API {api_name} is already enabled for project {project_id}.")
    else:
        # Enable the API if it is not enabled
        request = service_usage_v1.EnableServiceRequest(
            name=f'projects/{project_id}/services/{api_name}'
        )
        operation = client.enable_service(request)
        operation.result()  # Wait for the operation to complete
        logging.info(f"Enabled API {api_name} for project {project_id}.")

def get_organization_id() -> str:
    """
    Retrieves the organization ID using the Resource Manager API.
    
    Returns:
        str: The organization ID.
    """
    client = resourcemanager_v3.OrganizationsClient(credentials=credentials)
    orgs = client.search_organizations()
    for org in orgs:
        logging.info(f"Found organization: {org.display_name} ({org.name})")
        return org.name
    raise Exception("No organizations found.")

def get_audit_logs(organization_id: str, start_time: datetime, end_time: datetime, max_results: int, filter_str: str = None) -> list:
    """
    Retrieves and saves audit logs for the entire organization.
    
    Args:
        organization_id (str): The organization ID.
        start_time (datetime): The start time for the logs.
        end_time (datetime): The end time for the logs.
        max_results (int): The maximum number of results to retrieve.
        filter_str (str, optional): The filter string for the logs. Defaults to None.
    
    Returns:
        list: A list of audit log entries.
    """
    client = google.cloud.logging.Client(credentials=credentials)
    
    base_filter = (
        f'timestamp>="{start_time.isoformat()}Z" '
        f'timestamp<="{end_time.isoformat()}Z"'
    )
    
    if filter_str:
        filter_str = f'{filter_str} {base_filter}'
    else:
        filter_str = base_filter
    
    logging.info(f"Using filter: {filter_str}")
    
    entries = client.list_entries(
        filter_=filter_str,
        order_by=DESCENDING,
        max_results=max_results
    )
    
    logs = []
    for entry in entries:
        logs.append(entry.to_api_repr())
    
    return logs

def save_audit_logs(logs: list, filename: str):
    """
    Saves the retrieved audit logs to a JSON file.
    
    Args:
        logs (list): The list of audit log entries.
        filename (str): The name of the file to save logs to.
    """
    with open(filename, 'w') as file:
        json.dump(logs, file, indent=2)
    logging.info(f"All logs have been saved to {filename}")

def main(start_time: datetime, end_time: datetime, max_results: int, filter_str: str, filename: str):
    try:
        api_name = 'cloudresourcemanager.googleapis.com'
        enable_api(project_id, api_name)

        organization_id = get_organization_id()
        logging.info(f"Organization ID: {organization_id}")
        
        logs = get_audit_logs(organization_id, start_time, end_time, max_results, filter_str)
        logging.info(f"Retrieved {len(logs)} log entries.")
        
        save_audit_logs(logs, filename)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
