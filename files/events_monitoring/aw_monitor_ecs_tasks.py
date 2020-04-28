import json
import boto3
import os


SNS_TOPIC = os.environ.get("SNS_TOPIC", "arn:aws:sns:us-east-2:100000000000:aw_devops_dev")


def check_containers_exit_codes(message, event):
    """
        Check task container(s) exit code(s)
        Send notification if:
          - containers doesn't contain "exitCode"
          - exit code not in (0, 1, 127, 241) (all known exit codes for us)
    """
    failed = []
    
    for container in event["detail"]["containers"]:
        if "exitCode" in container and container["exitCode"] not in (0, 1, 127, 241):
            if "reason" in container:
                msg = f"container: '{container['name']}', exit code: {container['exitCode']}, reason: '{container['reason']}'"
            else:
                msg = f"container: '{container['name']}', exit code: {container['exitCode']}"
            failed.append(msg)
        elif "exitCode" not in container:
            if "reason" in container:
                msg = f"container: '{container['name']}', reason: '{container['reason']}'"
            else:
                msg = f"container: '{container['name']}' - no exit code, strange!"
            failed.append(msg)

    if len(failed) > 0:
        task_definition = event["detail"]["group"].split(":")[1]
        region = event["region"]

        message.append(f"During running task {task_definition} some of containers have failed:")
        message.append("\n".join(failed))
        message.append("")


def check_task_stop_status(message, event):
    stop_status = event["detail"]["stopCode"]
    if stop_status != "EssentialContainerExited":
        message.append(f"Task stop status: {stop_status}")
        message.append("")


def lambda_handler(event, context):
    if event["source"] != "aws.ecs":
        raise ValueError("Function only supports input from events with a source type of: aws.ecs")

    if event["detail-type"] != "ECS Task State Change":
        raise ValueError("detail-type for event is not a supported type. Exiting without saving event.")

    region = event["region"]
    task_id = event["detail"]["taskArn"].split("/")[1]
    task_definition = event["detail"]["group"].split(":")[1]

    message = []

    try:
        check_containers_exit_codes(message, event)
        check_task_stop_status(message, event)
    except Exception as e:
        message.append(f"Exception: {e}")

    if len(message) > 0:
        message.append(f"Task id: {task_id}")
        message.append("")
        message.append(f"Link to task logs: https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logEventViewer:group=/ecs/aw-etl;stream=ecs/{task_definition}/{task_id}")
        message.append("")
        message.append(f"Event: {event}")

        boto3.client("sns").publish(
            TopicArn=SNS_TOPIC,
            Subject=f"Task {task_definition}: one or more container(s) or task failed",
            Message="\n".join(message)
        )


def test():
    import logging
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.DEBUG, datefmt='%Y/%m/%d %H:%M:%S')

    ###exit code = 137
    event_json = '{"version":"0","id":"cfe11315-fb85-5643-f1ca-c07ae05c4806","detail-type":"ECS Task State Change","source":"aws.ecs","account":"100000000000","time":"2020-04-20T14:01:38Z","region":"us-east-2","resources":["arn:aws:ecs:us-east-2:100000000000:task/b43cbf35-5e5b-4656-8ab1-69d846fd6018"],"detail":{"attachments":[{"id":"9718ed7e-0efe-4ba2-aef5-f790a600621e","type":"eni","status":"DELETED","details":[{"name":"subnetId","value":"subnet-0fe33f63563c0bb0d"},{"name":"networkInterfaceId","value":"eni-0fd8590601adaae50"},{"name":"macAddress","value":"02:1a:24:6e:08:04"},{"name":"privateIPv4Address","value":"172.32.0.220"}]}],"availabilityZone":"us-east-2a","clusterArn":"arn:aws:ecs:us-east-2:100000000000:cluster/aw-etl","containers":[{"containerArn":"arn:aws:ecs:us-east-2:100000000000:container/9179ea19-091c-45ac-9856-18dda58f64ed","exitCode":1,"lastStatus":"STOPPED","name":"TEST","image":"100000000000.dkr.ecr.us-east-2.amazonaws.com/aw-etl-scripts:latest","imageDigest":"sha256:c1d1ec7e57a2c8f43676af28abc9f3d3c060947f83b4b31080723812e42d88d8","runtimeId":"f618019854ed240877157d651faf720f471734ca573c0652f250e27df48aa021","taskArn":"arn:aws:ecs:us-east-2:100000000000:task/b43cbf35-5e5b-4656-8ab1-69d846fd6018","networkInterfaces":[{"attachmentId":"9718ed7e-0efe-4ba2-aef5-f790a600621e","privateIpv4Address":"172.32.0.220"}],"cpu":"0"},{"containerArn":"arn:aws:ecs:us-east-2:100000000000:container/9179ea19-091c-45ac-9856-18dda58f64ed","exitCode":137,"lastStatus":"STOPPED","name":"TEST2","reason":"test reason","image":"100000000000.dkr.ecr.us-east-2.amazonaws.com/aw-etl-scripts:latest","imageDigest":"sha256:c1d1ec7e57a2c8f43676af28abc9f3d3c060947f83b4b31080723812e42d88d8","runtimeId":"f618019854ed240877157d651faf720f471734ca573c0652f250e27df48aa021","taskArn":"arn:aws:ecs:us-east-2:100000000000:task/b43cbf35-5e5b-4656-8ab1-69d846fd6018","networkInterfaces":[{"attachmentId":"9718ed7e-0efe-4ba2-aef5-f790a600621e","privateIpv4Address":"172.32.0.220"}],"cpu":"0"}],"createdAt":"2020-04-20T14:00:28.849Z","launchType":"FARGATE","cpu":"256","memory":"512","desiredStatus":"STOPPED","group":"family:aw-test-test-test","lastStatus":"STOPPED","overrides":{"containerOverrides":[{"name":"aw-test-test-test"}]},"connectivity":"CONNECTED","connectivityAt":"2020-04-20T14:00:32.734Z","pullStartedAt":"2020-04-20T14:00:46.426Z","startedAt":"2020-04-20T14:00:58.426Z","startedBy":"events-rule/aw-test-test-test","stoppingAt":"2020-04-20T14:01:15.514Z","stoppedAt":"2020-04-20T14:01:38.344Z","pullStoppedAt":"2020-04-20T14:00:53.426Z","executionStoppedAt":"2020-04-20T14:01:05Z","stoppedReason":"Essential container in task exited","stopCode":"EssentialContainerExited","updatedAt":"2020-04-20T14:01:38.344Z","taskArn":"arn:aws:ecs:us-east-2:100000000000:task/TESTTEST-TEST-TEST-TEST-TESTTESTTEST","taskDefinitionArn":"arn:aws:ecs:us-east-2:100000000000:task-definition/aw-test-test-test:60","version":5,"platformVersion":"1.3.0"}}'

    # ###no exit code
    # event_json = '{"version":"0","id":"cfe11315-fb85-5643-f1ca-c07ae05c4806","detail-type":"ECS Task State Change","source":"aws.ecs","account":"100000000000","time":"2020-04-20T14:01:38Z","region":"us-east-2","resources":["arn:aws:ecs:us-east-2:100000000000:task/b43cbf35-5e5b-4656-8ab1-69d846fd6018"],"detail":{"attachments":[{"id":"9718ed7e-0efe-4ba2-aef5-f790a600621e","type":"eni","status":"DELETED","details":[{"name":"subnetId","value":"subnet-0fe33f63563c0bb0d"},{"name":"networkInterfaceId","value":"eni-0fd8590601adaae50"},{"name":"macAddress","value":"02:1a:24:6e:08:04"},{"name":"privateIPv4Address","value":"172.32.0.220"}]}],"availabilityZone":"us-east-2a","clusterArn":"arn:aws:ecs:us-east-2:100000000000:cluster/aw-etl","containers":[{"containerArn":"arn:aws:ecs:us-east-2:100000000000:container/9179ea19-091c-45ac-9856-18dda58f64ed","reason":"Some fake fail reason","lastStatus":"STOPPED","name":"TEST","image":"100000000000.dkr.ecr.us-east-2.amazonaws.com/aw-etl-scripts:latest","imageDigest":"sha256:c1d1ec7e57a2c8f43676af28abc9f3d3c060947f83b4b31080723812e42d88d8","runtimeId":"f618019854ed240877157d651faf720f471734ca573c0652f250e27df48aa021","taskArn":"arn:aws:ecs:us-east-2:100000000000:task/b43cbf35-5e5b-4656-8ab1-69d846fd6018","networkInterfaces":[{"attachmentId":"9718ed7e-0efe-4ba2-aef5-f790a600621e","privateIpv4Address":"172.32.0.220"}],"cpu":"0"}],"createdAt":"2020-04-20T14:00:28.849Z","launchType":"FARGATE","cpu":"256","memory":"512","desiredStatus":"STOPPED","group":"family:aw-test-test-test","lastStatus":"STOPPED","overrides":{"containerOverrides":[{"name":"aw-test-test-test"}]},"connectivity":"CONNECTED","connectivityAt":"2020-04-20T14:00:32.734Z","pullStartedAt":"2020-04-20T14:00:46.426Z","startedAt":"2020-04-20T14:00:58.426Z","startedBy":"events-rule/aw-test-test-test","stoppingAt":"2020-04-20T14:01:15.514Z","stoppedAt":"2020-04-20T14:01:38.344Z","pullStoppedAt":"2020-04-20T14:00:53.426Z","executionStoppedAt":"2020-04-20T14:01:05Z","stoppedReason":"Essential container in task exited","stopCode":"SomeStrangeStopCode","updatedAt":"2020-04-20T14:01:38.344Z","taskArn":"arn:aws:ecs:us-east-2:100000000000:task/TESTTEST-TEST-TEST-TEST-TESTTESTTEST","taskDefinitionArn":"arn:aws:ecs:us-east-2:100000000000:task-definition/aw-test-test-test:60","version":5,"platformVersion":"1.3.0"}}'

    event = json.loads(event_json)
    lambda_handler(event, None)
