import json
import boto3
import os
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')


def handler(event, context):
    data = {}

    topic_arn = common.get_env_variable(os.environ, 'TOPIC_ARN')
    table_name = common.get_env_variable(os.environ, 'NOTFOUND_TABLE_NAME')

    item_count = get_item_count(table_name)

    if item_count > 0:
        send_response = send_msg(topic_arn, item_count)
        data['alert_sent'] = send_response
    else:
        data['alert_sent'] = False

    data['items'] = item_count

    response = common.create_response(200, json.dumps(data))

    return response


def get_item_count(table_name):
    log.info("Scanning table: {}".format(table_name))

    try:
        response = dynamodb.scan(
            TableName=table_name,
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    items = response['Items']
    item_count = len(items)
    log.info("Number of items in table: {}".format(item_count))

    return item_count


def send_msg(topic, item_count):
    log.info("Sending SMS message with item count: {}".format(item_count))
    try:
        response = sns.publish(
            TopicArn=topic,
            Message='There are ' + str(item_count) + ' items in the NotFound table.',
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'Ewelists'
                }
            }
        )
    except ClientError as e:
        raise Exception("Could not send SMS alert: " + e.response['Error']['Message'])

    log.info("SMS sent! Message ID: " + response['MessageId'])

    return True
