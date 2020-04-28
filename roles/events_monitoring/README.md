## Role `events_monitoring`
Creates lambdas and all required by them stuff to monitor Cloudwatch Events.

#### Variables example
```yml
    monitoring_tasks_files_path: "files/events_monitoring"
    monitoring_tasks:
    - name: aw_monitor_step_functions
        environment:
          SNS_TOPIC: "arn:aws:sns:us-east-2:100000000000:aw_notifications"
        tags:
          contact: "aleksandr_samodelkin@epam.com"
        cw_rule_name: AWMonitorStepFunctions
        cw_rule_description: Check ABORTED, FAILED and TIMED_OUT status and send notification
```

#### Role expects a couple of files
| Description | File | 
| --- | --- |
| Lambda function | some_lambda.py |
| Event pattern for CloudWatch rule | some_lambda.event_pattern.json |
| IAM policy for Lambda function | some_lambda.iam_role.json |

All files should be placed in `monitoring_tasks_files_path` directory.

#### Requirements
* Ansible ~=2.8.0 (2.8.x)
  * zip installed on Ansible host
  * boto3
* lambdas
  * python 3.8+
  * handler: some_lambda.lambda_handler
