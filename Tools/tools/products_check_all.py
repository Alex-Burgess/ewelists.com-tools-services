import json
import os
from tools import common, logger
from tools.common_entities import Product
from botocore.exceptions import ClientError

log = logger.setup_logger()


def handler(event, context):
    try:
        id = common.get_path_id(event)

        env = common.get_env_variable(os.environ, 'ENVIRONMENT')
        role_prefix = common.get_env_variable(os.environ, 'CROSS_ACCOUNT_ROLE')
        account_ids = {
            common.get_env_variable(os.environ, 'PRODUCTS_TEST_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_TEST'),
            common.get_env_variable(os.environ, 'PRODUCTS_STAGING_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_STAGING'),
            common.get_env_variable(os.environ, 'PRODUCTS_PROD_TABLE_NAME'): common.get_env_variable(os.environ, 'ACCOUNT_ID_PROD')
        }

        primary_env = common.get_env_variable(os.environ, 'PRIMARY_ENVIRONMENT')
        update_envs = common.get_env_variable(os.environ, 'UPDATE_ENVIRONMENTS')

        all_tables = {
            'test': common.get_env_variable(os.environ, 'PRODUCTS_TEST_TABLE_NAME'),
            'staging': common.get_env_variable(os.environ, 'PRODUCTS_STAGING_TABLE_NAME'),
            'prod': common.get_env_variable(os.environ, 'PRODUCTS_PROD_TABLE_NAME')
        }

        # Step 1: Update tables object to only include  non-primary environments.
        primary_table, secondary_tables = split_tables(all_tables, primary_env, update_envs)

        # Step 2: Search primary table for object.
        product = get_item(primary_table, account_ids, role_prefix, env, id)
        data = {"product": product}

        # Step 3: Search secondary environments for object and confirm if exist and if identical.
        check_results = check_environments(secondary_tables, account_ids, role_prefix, env, product.copy())
        data["test_environment_states"] = check_results

        response = common.create_response(200, json.dumps(data))

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def split_tables(tables, primary_env, update_envs):
    primary_table = tables[primary_env]

    update_tables = {}
    for env in update_envs.split(","):
        update_tables[env] = tables[env]

    return primary_table, update_tables


def check_environments(tables, account_ids, role_prefix, env, product):
    results = {}

    product.pop('priceCheckedDate', None)

    for environment in tables:
        table = tables[environment]
        try:
            env_product = get_item(table, account_ids, role_prefix, env, product['productId'])
            env_product.pop('priceCheckedDate', None)

            if env_product == product:
                results[environment] = "IN SYNC"
            else:
                results[environment] = "NOT IN SYNC"
        except Exception as e:
            if str(e) == "No product exists with id: {}".format(product['productId']):
                results[environment] = "DOES NOT EXIST"
            else:
                raise e

    return results


def get_item(table_name, account_ids, role_prefix, env, id):
    log.info("Querying table {} for product id: {}".format(table_name, id))
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

    log.info("Get item response: {}".format(response))

    if 'Item' not in response:
        raise Exception("No product exists with id: {}".format(id))

    product = Product(response['Item']).get_product()

    return product
