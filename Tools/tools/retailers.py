from urllib.parse import urlparse


map = {
    'amzn.to': 'amazon.co.uk'
}


def get(url):
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    elif domain.startswith('www2.'):
        domain = domain[5:]

    if domain in map:
        domain = map[domain]

    return domain
