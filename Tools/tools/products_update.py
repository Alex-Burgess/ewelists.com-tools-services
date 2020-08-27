import json
import os
import boto3
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        table_name = common.get_env_variable(os.environ, 'PRODUCTS_TABLE_NAME')

        id = common.get_path_id(event)
        product = common.new_product_details(event)
        put_product(table_name, id, product)

        data = {'updated': True}

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def put_product(table_name, id, new_product):
    try:
        log.info("Product item to be put in table: {}".format(new_product))
        response = dynamodb.update_item(
            TableName=table_name,
            Key={'productId': {'S': id}},
            UpdateExpression="set retailer = :r, brand = :b, details = :d, price = :p, productUrl = :u, imageUrl = :i, priceCheckedDate = :c",
            ExpressionAttributeValues={
                ':r': {'S': new_product["retailer"]},
                ':b': {'S': new_product["brand"]},
                ':d': {'S': new_product["details"]},
                ':p': {'S': new_product["price"]},
                ':u': {'S': new_product["productUrl"]},
                ':i': {'S': new_product["imageUrl"]},
                ':c': {'S': common.currentTimestamp()}
            },
            ReturnValues="UPDATED_NEW"
        )

        log.info("Attributes updated: " + json.dumps(response['Attributes']))
    except ClientError as e:
        log.error("Product could not be updated: {}".format(e))
        raise Exception('Product could not be updated.')

    return True
