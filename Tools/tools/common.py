# A collection of methods that are common across all modules.
import json
import boto3
from datetime import datetime
from tools import logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


def currentTimestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_env_variable(osenv, name):
    try:
        variable = osenv[name]
        log.info(name + " environment variable value: " + variable)
    except KeyError:
        raise Exception(name + ' environment variable not set correctly.')

    return variable


def create_response(code, body):
    log.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response


def get_table_names(osenv):
    try:
        products_name = osenv['PRODUCTS_TABLE_NAME']
        notfound_name = osenv['NOTFOUND_TABLE_NAME']
        lists_name = osenv['LISTS_TABLE_NAME']

        log.info("Table environment variables. PRODUCTS_TABLE_NAME: {}. NOTFOUND_TABLE_NAME: {}. LISTS_TABLE_NAME: {}.".format(products_name, notfound_name, lists_name))
    except KeyError:
        raise Exception('Table environment variables not set correctly.')

    return products_name, notfound_name, lists_name


def get_path_id(event):
    try:
        id = event['pathParameters']['id']
        log.info("Path parameter ID: " + id)
    except Exception:
        raise Exception('API Event did not contain a path parameter called ID.')

    return id


def new_product_details(event):
    product = {}

    expected_keys = ["brand", "details", "retailer", "imageUrl", "productUrl", "price"]

    try:
        body = json.loads(event['body'])
    except Exception:
        raise Exception('API Event body did not exist.')

    for key in expected_keys:
        if key in body:
            product[key] = body[key]
        else:
            raise Exception('API Event body did not contain the ' + key + '.')

    log.info("Product details from body: " + json.dumps(product))

    return product


def check_environments(event):
    log.info("Check which environments to create new product in.")

    environments = []

    try:
        body = json.loads(event['body'])
    except Exception:
        raise Exception('API Event body did not exist.')

    for key in ['test', 'staging', 'prod']:
        if key in body:
            if body[key]:
                environments.append(key)
        else:
            raise Exception('API Event body did not contain the ' + key + ' attribute.')

    log.info("Environments to update are: {}.".format(environments))

    return environments


def cross_account_role_required(table_name, env):
    env = '-' + env

    if env not in table_name:
        return True
    else:
        return False


def get_dynamodb_client(table_name, account_ids, role_prefix, env):
    if cross_account_role_required(table_name, env):
        log.info("Cross account role required to connect to table in different account. Environment: {} Table: {}.".format(env, table_name))
        role_arn = "arn:aws:iam::" + account_ids[table_name] + ":role/Tools-Service-Cross-Account-Exection-Role" + "-" + env

        try:
            sts_connection = boto3.client('sts')
            acct_b = sts_connection.assume_role(
                RoleArn=role_arn,
                RoleSessionName="cross_acct_lambda"
            )

            ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
            SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
            SESSION_TOKEN = acct_b['Credentials']['SessionToken']

            # create service client using the assumed role credentials, e.g. S3
            client = boto3.client(
                'dynamodb',
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                aws_session_token=SESSION_TOKEN,
            )

            return client
        except ClientError as e:
            raise Exception("Error assuming role ({}): {}".format(role_arn, e))
    else:
        log.info("Returning simple dynamodb client. Environment: {} Table: {}.".format(env, table_name))
        return boto3.client('dynamodb')
