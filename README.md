# CloudLogCollector

This project provides a set of scripts to collect and save audit logs from various cloud providers, including Google Cloud Platform (GCP), Microsoft Azure, Microsoft Entra ID (formerly Azure AD), and Amazon Web Services (AWS).

## Features

- **GCP Audit Logs**: Retrieve and save GCP audit logs within a specified time range.
- **Azure Activity Logs**: Retrieve and save Azure activity logs within a specified time range.
- **Microsoft Entra ID Sign-In Logs**: Retrieve and save Microsoft Entra ID sign-in logs within a specified time range.
- **AWS CloudTrail Events**: Retrieve and save AWS CloudTrail events within a specified time range for given accounts and roles.

## Prerequisites

- Python 3.x
- Google Cloud SDK
- Azure SDK for Python
- AWS SDK for Python (Boto3)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/cloud-audit-log-collector.git
    cd cloud-audit-log-collector
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### GCP Audit Logs

To retrieve and save GCP audit logs:

```python
from datetime import datetime, timedelta
import gcp_audit_logs

now = datetime.utcnow()
yesterday = now - timedelta(days=1)

gcp_audit_logs.enable_api('your-project-id', 'logging.googleapis.com')
gcp_audit_logs.get_gcp_logs(yesterday, now, 500, filename='gcp_audit_logs.json')
```

### Azure Activity Logs
To retrieve and save Azure activity logs:
```python

from datetime import datetime, timedelta
import azure_activity_logs

now = datetime.utcnow()
yesterday = now - timedelta(days=1)

azure_activity_logs.get_azure_logs(yesterday, now, filename='azure_events.json')

```



### Microsoft Entra ID Sign-In Logs
To retrieve and save Microsoft Entra ID sign-in logs:
```python
from datetime import datetime, timedelta
import entraid_signin_logs

now = datetime.utcnow()
yesterday = now - timedelta(days=1)

entra_id_signin_logs.get_entra_id_signin_logs(yesterday, now, filename='entra_id_signins.json')

```


### AWS CloudTrail Events
To retrieve and save AWS CloudTrail events:
```python
from datetime import datetime, timedelta
import aws_cloudtrail_events

now = datetime.utcnow()
yesterday = now - timedelta(days=1)

aws_cloudtrail_events.get_aws_cloudtrail_events(['account-id-1', 'account-id-2'], 'role-name', yesterday, now, filename='aws_events.json')
```