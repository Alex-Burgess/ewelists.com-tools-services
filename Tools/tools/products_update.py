import json
import os
import time
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


def handler(event, context):
    try:
        env = common.get_env_variable(os.environ, 'ENVIRONMENT')
        role_prefix = common.get_env_variable(os.environ, 'CROSS_ACCOUNT_ROLE')
        account_ids = {
            common.get_env_variable(os.environ, 'PRODUCTS_TEST_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_TEST'),
            common.get_env_variable(os.environ, 'PRODUCTS_STAGING_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_STAGING'),
            common.get_env_variable(os.environ, 'PRODUCTS_PROD_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_PROD')
        }

        tables = {
            'test': common.get_env_variable(os.environ, 'PRODUCTS_TEST_TABLE_NAME'),
            'staging': common.get_env_variable(os.environ, 'PRODUCTS_STAGING_TABLE_NAME'),
            'prod': common.get_env_variable(os.environ, 'PRODUCTS_PROD_TABLE_NAME')
        }

        environments_to_update = common.check_environments(event)

        id = common.get_path_id(event)
        product = common.new_product_details(event)

        # error, data = make_changes(tables, environments_to_update, id, product, env)
        error, data = make_changes(tables, account_ids, role_prefix, env, environments_to_update, id, product)

        if error:
            response = common.create_response(500, json.dumps(data))
        else:
            response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def make_changes(tables, account_ids, role_prefix, env, environments_to_update, id, product):
    results = {}
    error = False

    for env_to_update in environments_to_update:
        try:
            table = tables[env_to_update]
            exists = get_product(table, account_ids, role_prefix, env, id)
            if exists:
                update_product(table, account_ids, role_prefix, env, id, product)
                results[env_to_update] = "Updated: " + id
            else:
                put_product(table, account_ids, role_prefix, env, id, product)
                results[env_to_update] = "Created: " + id
        except Exception as e:
            log.error("Exception: {}".format(e))
            results[env_to_update] = "Failed: Unexpected error when updating"
            error = True

    return error, results


def get_product(table_name, account_ids, role_prefix, env, id):
    log.info("Querying table for product id: {}".format(id))
    key = {'productId': {'S': id}}

    try:
        dynamodb = common.get_dynamodb_client(table_name, account_ids, role_prefix, env)
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    log.info("Get item response ({}): {}".format(table_name, response))

    if 'Item' not in response:
        return False

    return True


def update_product(table_name, account_ids, role_prefix, env, id, new_product):
    try:
        log.info("Product item to be put in table: {}".format(new_product))
        dynamodb = common.get_dynamodb_client(table_name, account_ids, role_prefix, env)
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


def put_product(table_name, account_ids, role_prefix, env, id, product):
    create_object = product_details(product, id)
    try:
        log.info("Product item to be put in table: {}".format(product))
        dynamodb = common.get_dynamodb_client(table_name, account_ids, role_prefix, env)
        dynamodb.put_item(TableName=table_name, Item=create_object)
    except ClientError as e:
        log.error("Product could not be created ({}): {}".format(table_name, e))
        raise Exception("Product could not be created ({}).".format(table_name))

    return True


def product_details(product, id):
    try:
        product = {
            'productId': {'S': id},
            'retailer': {'S': product['retailer']},
            'brand': {'S': product['brand']},
            'details': {'S': product['details']},
            'price': {'S': product['price']},
            'priceCheckedDate': {'S': common.currentTimestamp()},
            'productUrl': {'S': product['productUrl']},
            'imageUrl': {'S': product['imageUrl']},
            'createdAt': {'N': str(int(time.time()))}
        }
    except Exception:
        raise Exception('API Event body did not contain correct attributes.')

    return product
