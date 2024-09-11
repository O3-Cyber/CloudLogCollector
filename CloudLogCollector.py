"""
Script to run the organization-wide audit log export modules for various cloud providers.

This script includes functions to retrieve and save audit logs from:
- Google Cloud Platform (GCP)
- Microsoft Azure
- Microsoft Entra ID (formerly Azure AD)
- Amazon Web Services (AWS)
"""

import gcp_audit_logs
import azure_activity_logs
import entraid_signin_logs
import aws_cloudtrail_events
from datetime import datetime, timedelta

def get_gcp_logs(start_time: datetime, end_time: datetime, max_results: int, filter_str: str = None, filename: str = 'gcp_audit_logs.json'):
    gcp_audit_logs.main(start_time, end_time, max_results, filter_str, filename)

def get_azure_logs(start_time: datetime, end_time: datetime, filename: str = 'azure_events.json'):
    logs = azure_activity_logs.main(start_time.isoformat(), end_time.isoformat())
    azure_activity_logs.save_audit_logs(logs, filename)

def get_entra_id_signin_logs(start_time: datetime, end_time: datetime, filename: str = 'entra_id_signins.json'):
    logs = entraid_signin_logs.main(start_time, end_time)
    entraid_signin_logs.save_sign_in_logs(logs, filename)

def get_aws_cloudtrail_events(account_list: list, role_name: str, start_time: datetime, end_time: datetime, filename: str = 'aws_events.json'):
    events = aws_cloudtrail_events.main(account_list, role_name, start_time, end_time)
    aws_cloudtrail_events.save_cloudtrail_logs(events, filename)

if __name__ == "__main__":
    endtime = datetime.utcnow()
    starttime = endtime - timedelta(days=30)

    get_gcp_logs(starttime, endtime, 5000, filename='gcp_audit_logs.json')
    get_azure_logs(starttime, endtime, filename='azure_events.json')
    get_entra_id_signin_logs(starttime, endtime, filename='entra_id_signins.json')
    get_aws_cloudtrail_events(['012345678901', '000000000001'], 'SecurityAuditRole', starttime, endtime, filename='aws_events.json')