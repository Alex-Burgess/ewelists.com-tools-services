import json
import os
import boto3
import time
import uuid
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        table_name = common.get_env_variable(os.environ, 'PRODUCTS_TABLE_NAME')

        create_obj = common.new_product_details(event)
        product = product_details(create_obj)
        put_product(table_name, product)

        data = {'productId': product['productId']['S']}

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def put_product(table_name, product):
    try:
        log.info("Product item to be put in table: {}".format(product))
        dynamodb.put_item(TableName=table_name, Item=product)
    except ClientError as e:
        log.error("Product could not be created: {}".format(e))
        raise Exception('Product could not be created.')

    return True


def product_details(create_obj):
    try:
        product_id = str(uuid.uuid4())
        product = {
            'productId': {'S': product_id},
            'retailer': {'S': create_obj['retailer']},
            'brand': {'S': create_obj['brand']},
            'details': {'S': create_obj['details']},
            'price': {'S': create_obj['price']},
            'priceCheckedDate': {'S': common.currentTimestamp()},
            'productUrl': {'S': create_obj['productUrl']},
            'imageUrl': {'S': create_obj['imageUrl']},
            'createdAt': {'N': str(int(time.time()))}
        }
    except Exception:
        raise Exception('API Event body did not contain correct attributes.')

    return product
