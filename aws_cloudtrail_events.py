"""
AWS CloudTrail Events Module

This module retrieves and saves CloudTrail logs for specified AWS accounts. It assumes a specified role in each account,
iterates through all available regions, and collects CloudTrail events within the last 24 hours.

Functions:
- assume_role(account_id, role_name): Assumes the specified role in the given account and returns a boto3 session.
- get_cloudtrail_logs(account_list, role_name, start_time, end_time): Retrieves and saves CloudTrail logs for specified AWS accounts.
"""

import boto3
import json
from botocore.exceptions import ClientError

def assume_role(account_id, role_name):
    """
    Assume the specified role in the given account and return a session.

    Parameters:
    - account_id: AWS account ID.
    - role_name: The role to assume in the account.

    Returns:
    A boto3 session using the assumed role credentials.
    """
    sts_client = boto3.client('sts')

    print(f"Assuming role in account: {account_id}")

    # Assume the role in the target account
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='CloudLogCollector'
    )

    # Extract the temporary credentials
    credentials = assumed_role['Credentials']

    # Initialize a session using the assumed role credentials
    session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    return session

def get_cloudtrail_logs(account_list, role_name, start_time, end_time):
    """
    Retrieve and save CloudTrail logs for specified AWS accounts.

    Parameters:
    - account_list: List of AWS account IDs.
    - role_name: The role to assume in each account.
    - start_time: The start time for the CloudTrail logs.
    - end_time: The end time for the CloudTrail logs.

    Returns:
    List of collected CloudTrail events.
    """
    all_events = []

    # Loop through all account IDs and collect CloudTrail logs
    for account_id in account_list:
        session = assume_role(account_id, role_name)

        # Get the list of all available regions for CloudTrail
        ec2_client = session.client('ec2')
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

        # Loop through all regions and collect CloudTrail events
        for region in regions:
            print(f"Collecting events from region: {region}")

            # Initialize the CloudTrail client for the current region using the session
            cloudtrail_client = session.client('cloudtrail', region_name=region)

            next_token = None
            while True:
                try:
                    if next_token:
                        response = cloudtrail_client.lookup_events(
                            StartTime=start_time,
                            EndTime=end_time,
                            NextToken=next_token
                        )
                    else:
                        response = cloudtrail_client.lookup_events(
                            StartTime=start_time,
                            EndTime=end_time
                        )

                    # Get the events
                    events = response.get('Events', [])

                    # Normalize the CloudTrailEvent field and convert datetime objects to strings
                    for event in events:
                        if 'CloudTrailEvent' in event:
                            event['CloudTrailEvent'] = json.loads(event['CloudTrailEvent'])
                        if 'EventTime' in event:
                            event['EventTime'] = event['EventTime'].isoformat()

                    # Add the events to the all_events list
                    all_events.extend(events)

                    print(f"Collected {len(events)} events from region {region}")

                    # Check if there is a next token
                    next_token = response.get('NextToken')
                    if not next_token:
                        break
                except ClientError as e:
                    if e.response['Error']['Code'] == 'UnrecognizedClientException':
                        print(f"UnrecognizedClientException in region {region}: {e}")
                    else:
                        print(f"An error occurred in region {region}: {e}")
                    break

    return all_events

def save_cloudtrail_logs(logs, filename):
    """
    Saves the retrieved CloudTrail logs to a JSON file.

    Parameters:
    - logs: The list of CloudTrail log entries.
    - filename: The name of the file to save logs to.
    """
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=2)
    print(f"CloudTrail logs saved to: {filename}")

def main(account_list, role_name, start_time, end_time):
    """
    Main function to retrieve and save CloudTrail logs for specified AWS accounts within a specified time range.

    Parameters:
    - account_list: List of AWS account IDs.
    - role_name: The role to assume in each account.
    - start_time: The start time for the CloudTrail logs.
    - end_time: The end time for the CloudTrail logs.
    """
    events = get_cloudtrail_logs(account_list, role_name, start_time, end_time)
    return events
