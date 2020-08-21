import json
import os
import boto3
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        table_name = common.get_env_variable(os.environ, 'NOTFOUND_TABLE_NAME')

        count = get_item_count(table_name)

        data = {"count": count}

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

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
