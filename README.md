# Filter K8s Audit Logs

## Abstract

This library provides a simple way to filter Kubernetes audit logs, if you, whit some reason, are not able to apply
audit policy directly at your cloud (e. g. in yandex cloud) and have to filter it with python script. 
Also you can use this library to analyze audit logs.
The library does not provide any service, it just give you easy way to filter audit logs in your python script
with ```AuditFilter``` class interfaces.

## Instalation

```bash
pip install k8s-audit-filter
```

## Usage

You can easly modify your python script to filter audit logs.
Just import ```AuditFilter``` class, init it with your ```audit-policy.yaml``` file and use it's methods.
See an example of modification
of [this script](<https://github.com/yandex-cloud/yc-solution-library-for-security/blob/master/auditlogs/export-k8s-to-s3/terraform/function/main.py>):

```python
import json

import os
import boto3
import string
import random

from datetime import datetime

from k8s_audit_filter import AuditFilter  # import AuditFilter class


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


client = boto3.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    region_name='ru-central1'
)


def handler(event, context):
    for log_data in event['messages']:

        full_log = []
        for log_entry in log_data['details']['messages']:
            kubernetes_log = json.loads(log_entry['message'])
            full_log.append(json.dumps(kubernetes_log))

        audit_filter = AuditFilter('path/to/audit_policy.yaml')  # init AuditFilter class with path to audit policy file
        filtered_log = [line for line in full_log if audit_filter.filter(full_log)]  # filter audit logs

        bucket_name = os.environ.get('BUCKET_NAME')
        object_key = 'AUDIT/' + os.environ.get('CLUSTER_ID') + '/' + datetime.now().strftime(
            '%Y-%m-%d-%H:%M:%S') + '-' + get_random_alphanumeric_string(5)
        object_value = '\n'.join(filtered_log)  # prepare data to load
        client.put_object(Bucket=bucket_name, Key=object_key, Body=object_value,
                          StorageClass='COLD')  # load data to cloud storage
```

Also you can update your policy dinamically, just use ```add_rule``` and ```remove_rule``` method:

```python
from k8s_audit_filter import AuditFilter

audit_filter = AuditFilter()  # init AuditFilter class with blink audit policy
audit_filter.add_rule({'level': 'Metadata'})
audit_filter.filter({'level': 'Metadata'})  # return True
audit_filter.remove_rule({'level': 'Metadata'})
audit_filter.filter({'level': 'Metadata'})  # return False
```

## Describing Audit Policy

You can use find the way to describe k8s audit policy rules in Official Kubernetes Documentation at <https://kubernetes.io/docs/reference/config-api/apiserver-audit.v1/>

See example of audit policy:

```yaml
apiVersion: audit.k8s.io/v1 # This is required.

kind: Policy

rules:
  # Include line in the audit log which contains verb "get" and have level "Metadata"
  - level: Metadata
    verbs:
      - "get"

  # Exclude line in the audit log which contains verb "create"
  - level: None
    verbs:
      - "create"

  - level: Request
    users:
      - "admin"

  - level: Request
    userGroups:
      - "system:admins"

```

## Describing Audit Policy in Python

If you want to describe audit policy in python, you can describe it in the same way as in yaml file with dict:

```python
from k8s_audit_filter import AuditFilter

audit_filter = AuditFilter()

rules = [
    {'level': 'Metadata', 'verbs': ['get']},
    {'level': 'None', 'verbs': ['create']},
    {'level': 'Request', 'users': ['admin']},
    {'level': 'Request', 'userGroups': ['system:admins']},
    {'level': 'Request', 'namespaces': ['kube-system']},
    {'level': 'RequestResponse',
     'resources': [
             {'group': '', 'resources': ['deployments'], 'resourceNames': ['pods']},
             {'group': 'apps', 'resources': ['leases'], 'resourceNames': ['test']}
         ]
     }
]
audit_filter.add_rules(rules)

```

## Supported Rules

Please note, that ```level``` is required field for every rule, and should have of one of next values:

- ```None``` - do not log events that match this rule (this is ExcludeRule)
- ```Metadata``` - log line marked as "Metadata"
- ```Request``` - log line marked as "Request"
- ```RequestResponse``` - log line marked as "RequestResponse"

The library supports the following rules k8s audit PolicyRules:

- ```level```
- ```verbs```
- ```users```
- ```userGroups```
- ```namespaces```
- ```resources``` - Partly supported. Please read about limitations below

## Limitations

The library does not support following k8s Audit rules:

- ```resources``` - please note, that unlike original k8s audit policy, empty string "" in "group" field will not return "core" group, but will return all groups
- ```nonResourceURLs``` - notResourceURLs are not declared explicitly in audit logs
- ```omitStages``` - now it does not discern any stages
- ```omitManagedFields``` - omitManagedFields is not declared explicitly in audit logs
