import json
import metadata_parser
import re
from urllib.parse import unquote
from tools import common, logger

log = logger.setup_logger()


attr_map = {
    'site_name': [
        {'og': 'site_name'},
        {'meta': 'og:site_name'},
        {'meta': 'og:site-name'}
    ],
    'image': [
        {'og': 'image:secure_url'},
        {'og': 'image'},
        {'meta': 'og:image:secure_url'},
        {'meta': 'og:image'}
    ],
    'title': [
        {'og': 'title'},
        {'meta': 'og:title'}
    ],
    'price': [
        {'meta': 'product:price:amount'},
        {'meta': 'og:price:amount'},
        {'og': 'price:amount'}
    ],
    'currency': [
        {'meta': 'product:price:currency'},
        {'meta': 'og:price:currency'},
        {'og': 'price:currency'}
    ]
}

title_regex_rules = [
    '^Buy ',
    ' at KIDLY UK$'
]


def handler(event, context):
    try:
        url = get_url(event)
        blocked_urls(url)
        data = query(url)
        data = parse_data(data)
        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def blocked_urls(url):
    if 'amazon' in url:
        raise Exception("Metadata query failed.")

    return False


def get_url(event):
    try:
        url = event['pathParameters']['url']
        log.info("Encoded URL: " + url)
    except Exception:
        raise Exception('API Event did not contain a Url in the path parameters.')

    url = unquote(url)
    log.info("Decoded URL: " + url)

    return url


def query(url):
    try:
        page = metadata_parser.MetadataParser(url=url, support_malformed=True)
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Metadata query failed.")

    return page.metadata


def parse_data(data):
    response = {}

    # Main rules
    for a in attr_map.keys():
        for key_names in attr_map[a]:
            for key in key_names.keys():
                name = key_names[key]
                if name in data[key]:
                    response[a] = update_response(response, a, data[key][name])

    # Exceptional rules
    if 'site_name' not in response:
        t = get_site_name_from_page_title(data)
        if t is not None:
            response['site_name'] = t

    if 'price' in response:
        response['price'] = check_price(response['price'])

    if 'title' in response:
        response['title'] = check_title(response['title'])
        response['title'] = check_title_regex_rules(response['title'])

    return response


def update_response(response, attribute, value):
    if attribute in response:
        return response[attribute]
    else:
        if type(value) == list:
            return value[0]

    return value


def get_site_name_from_page_title(data):
    if 'page' in data:
        if 'title' in data['page']:
            title = data['page']['title']
            if '|' in title:
                return title.split(' | ')[-1]

    return None


def check_price(price):
    p = "{:.2f}".format(float(price))
    return str(p)


def check_title(title):
    return title.split(' | ')[0]


def check_title_regex_rules(title):
    for rule in title_regex_rules:
        title = re.sub(rule, '', title)

    return title[:1].upper() + title[1:]
