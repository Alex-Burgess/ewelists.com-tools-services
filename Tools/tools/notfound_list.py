import json
import os
import boto3
from tools import common, logger
from tools.common_entities import Notfound
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        table_name = common.get_env_variable(os.environ, 'NOTFOUND_TABLE_NAME')

        response_items = get_items(table_name)
        items = parse_items(response_items)
        data = {"items": items}

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def get_items(table_name):
    log.info("Scanning table: {}".format(table_name))

    try:
        response = dynamodb.scan(
            TableName=table_name,
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    items = response['Items']
    log.info("Number of items in table: {}".format(len(items)))

    return items


def parse_items(response_items):
    log.info("Parsing number of items: " + str(len(response_items)))

    items = []

    for item in response_items:
        parsed_item = Notfound(item).get_product()
        items.append(parsed_item)

    return items
