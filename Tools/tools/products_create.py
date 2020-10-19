import json
import os
import time
import uuid
from tools import common, logger

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

        product_id = str(uuid.uuid4())
        create_obj = common.new_product_details(event)
        product = product_details(create_obj, product_id)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    results, errors = update_tables(tables, account_ids, role_prefix, env, environments_to_update, product)
    data = {'productId': product_id}

    for result in results:
        data[result] = results[result]

    if errors:
        data['error'] = 'There was an error when updating one or more environments.'
        response = common.create_response(500, json.dumps(data))
    else:
        response = common.create_response(200, json.dumps(data))

    return response


def update_tables(tables, account_ids, role_prefix, env, environments_to_update, product):
    results = {}
    errors = False

    for environment in environments_to_update:
        table = tables[environment]
        try:
            put_product(table, account_ids, role_prefix, env, product)
            results[environment] = "Success:" + product['productId']['S']
        except Exception as e:
            results[environment] = "Failed:" + str(e)
            errors = True

    return results, errors


def put_product(table_name, account_ids, role_prefix, env, product):
    log.info("Putting product item to table ({}): {}".format(table_name, product))

    try:
        dynamodb = common.get_dynamodb_client(table_name, account_ids, role_prefix, env)
        dynamodb.put_item(TableName=table_name, Item=product)
    except Exception as e:
        log.error("Product could not be created ({}): {}".format(table_name, e))
        raise Exception("Product could not be created ({}).".format(table_name))

    return True


def product_details(create_obj, product_id):
    try:
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
