from urllib.parse import urlparse


map = {
    'amzn.to': 'amazon.co.uk'
}


def get(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]

    if domain in map:
        domain = map[domain]

    return domain
