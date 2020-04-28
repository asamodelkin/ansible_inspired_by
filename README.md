# Ansible for ETL-related stuff

## How to run ansible and introduction
ansible-playbook <playbook> -i hosts

All variables are defined in `group_vars/all/<some_file>.yml`.
"Global" variables are defined in separate files according to their purpose & relation: `aws.yml`.

We have some playbooks with related variables placed in `group_vars/all/playbook_name.yml`.

## Playbooks
`events_monitoring.yml` - Cloudwatch Events monitoring setup for failed ECS tasks and Step Functions state machines stopped with non-successful states. Notifications will be sent to `SNS_TOPIC` environment variable defined in inventory. ZIPs of lambdas stored in git too to avoid lamdas re-creation each time we run playbook.

## Roles
[Role events_monitoring](roles/events_monitoring/README.md)
