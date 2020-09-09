import os
import boto3
import json
import requests
from urllib.parse import unquote
from tools import common, logger, retailers
from botocore.exceptions import ClientError

log = logger.setup_logger()

ssm = boto3.client('ssm')

probability_threshold = 0.09

# Map of api response attributes to returned attributes
attribute_map = {
    'brand': 'brand',
    'name': 'details',
    'mainImage': 'imageUrl',
    'offers': [
        {'price': 'price'},
        {'availability': 'availability'}
    ]
}


def handler(event, context):
    try:
        key_path = common.get_env_variable(os.environ, 'API_KEY_PATH')
        key = get_key(key_path)
        url = get_url(event)
        response = call_api(url, key)

        check_probability(response, probability_threshold)

        data = create_data(response)
        data = parse_details(data)
        data["retailer"] = retailers.get(url)

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def check_probability(response, threshold):
    if 'product' in response:
        if 'probability' in response['product']:
            if float(response['product']['probability']) > float(threshold):
                log.info("Probability ({}) was greater than threshold ({})".format(str(response['product']['probability']), threshold))
                return True

    log.error("Probability ({}) was lower than threshold ({})".format(str(response['product']['probability']), threshold))
    raise Exception('API Query returned with too low probability.')


def parse_details(data):
    if 'details' in data and 'brand' in data:
        if data['details'].startswith(data['brand']):
            chars_to_remove = len(data['brand']) + 1
            data['details'] = data['details'][chars_to_remove:]

    return data


def create_data(response):
    log.info("Creating data for response")
    return_data = {}

    if 'product' in response:
        product = response['product']
        map_func(attribute_map, return_data, product)

    return return_data


def map_func(map, return_data, product):
    for key, value in map.items():
        if key in product:
            if isinstance(value, str):
                # Reached end of attribute map and now have response attribute to returned attribute pair
                return_data[value] = product[key]
            elif isinstance(value, dict):
                map_func(value, return_data, product[key])
            elif isinstance(value, list):
                for val in value:
                    if isinstance(val, str):
                        pass
                    elif isinstance(val, list):
                        pass
                    else:
                        map_func(val, return_data, product[key][0])


def get_url(event):
    try:
        url = event['pathParameters']['url']
    except Exception:
        raise Exception('API Event did not contain a Url in the path parameters.')

    url = unquote(url)
    log.info("Decoded URL: " + url)

    return url


def get_key(path):
    try:
        response = ssm.get_parameter(Name=path, WithDecryption=True)
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Could not retrieve API secret from parameter store.")

    return response['Parameter']['Value']


def call_api(url, key):
    log.info("Caling API for url: " + url)

    try:
        json_response = post_request(url, key)
        log.info("Call API response: " + str(json_response))
    except Exception as e:
        log.error("Exception: {}".format(e))
        raise Exception("there was an issue with the Scrape Hub API call.")

    if "title" in json_response:
        if json_response["title"] == "Authentication token not provided or invalid":
            raise Exception("there was an issue with the Scrape Hub API call.")

    return json_response[0]


def post_request(url, key):
    try:
        response = requests.post(
            'https://autoextract.scrapinghub.com/v1/extract',
            auth=(key, ''),
            json=[{'url': url, 'pageType': 'product'}],
            timeout=45
        )
    except Exception as e:
        log.error("Exception caught when posting request.")
        raise Exception(e)

    return response.json()
