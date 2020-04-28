import json
import boto3
import os


SNS_TOPIC = os.environ.get("SNS_TOPIC", "arn:aws:sns:us-east-2:100000000000:aw_devops_dev")


def lambda_handler(event, context):
    if event["source"] != "aws.states":
        raise ValueError("Function only supports input from events with a source type of: aws.states")

    if event["detail-type"] != "Step Functions Execution Status Change":
        raise ValueError("detail-type for event is not a supported type. Exiting without saving event.")

    status = event["detail"]["status"]
    step_function = event["detail"]["stateMachineArn"].split(":")[-1]

    if status in ["FAILED", "TIMED_OUT", "ABORTED"]:
        msg = f"State machine '{step_function}' execution status: {status}"

        message = []
        message.append(msg)
        message.append("")
        message.append(f"Event: {event}")

        boto3.client("sns").publish(
            TopicArn=SNS_TOPIC,
            Subject=msg,
            Message="\n".join(message)
        )


def test():
    import logging
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG, datefmt='%Y/%m/%d %H:%M:%S')

    event_json = '''
        {
            "version": "0",
            "id": "18a988b9-acbc-15b6-9a33-076e778b1933",
            "detail-type": "Step Functions Execution Status Change",
            "source": "aws.states",
            "account": "100000000000",
            "time": "2020-04-27T10:53:00Z",
            "region": "us-east-2",
            "resources": [
                "arn:aws:states:us-east-2:100000000000:execution:AW-Flash-Report:1de9ffba-2a5e-34db-bbb7-3628c8b9c728_83fc8984-3d6e-80cd-71b5-85ac8b2b9eca"
            ],
            "detail": {
                "executionArn": "arn:aws:states:us-east-2:100000000000:execution:AW-Flash-Report:1de9ffba-2a5e-34db-bbb7-3628c8b9c728_83fc8984-3d6e-80cd-71b5-85ac8b2b9eca",
                "stateMachineArn": "arn:aws:states:us-east-2:100000000000:stateMachine:AW-Flash-Report",
                "name": "1de9ffba-2a5e-34db-bbb7-3628c8b9c728_83fc8984-3d6e-80cd-71b5-85ac8b2b9eca",
                "status": "FAILED",
                "startDate": 1587984037588,
                "stopDate": 1587984780905
            }
        }
    '''

    event = json.loads(event_json)
    lambda_handler(event, None)
