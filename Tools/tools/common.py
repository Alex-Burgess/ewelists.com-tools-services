# A collection of methods that are common across all modules.
import json
from tools import logger

log = logger.setup_logger()


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

    try:
        body = json.loads(event['body'])
    except Exception:
        raise Exception('API Event body did not exist.')

    if 'brand' in body:
        product['brand'] = body['brand']
    else:
        raise Exception('API Event body did not contain the product brand.')

    if 'details' in body:
        product['details'] = body['details']
    else:
        raise Exception('API Event body did not contain the product details.')

    if 'retailer' in body:
        product['retailer'] = body['retailer']
    else:
        raise Exception('API Event body did not contain the retailer.')

    if 'imageUrl' in body:
        product['imageUrl'] = body['imageUrl']
    else:
        raise Exception('API Event body did not contain the product imageUrl.')

    log.info("Product details from body: " + json.dumps(product))

    return product
