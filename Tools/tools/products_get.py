import json
import os
import boto3
from tools import common, logger
from tools.common_entities import Product
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        table_name = common.get_env_variable(os.environ, 'PRODUCTS_TABLE_NAME')
        id = common.get_path_id(event)

        product = get_item(table_name, id)

        response = common.create_response(200, json.dumps(product))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def get_item(table_name, id):
    log.info("Querying table for product id: {}".format(id))

    key = {'productId': {'S': id}}

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    log.info("Get item response: {}".format(response))

    if 'Item' not in response:
        raise Exception("No product exists with id: {}".format(id))

    product = Product(response['Item']).get_product()

    return product
