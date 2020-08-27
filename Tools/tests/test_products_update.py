import os
import json
from tools import products_update, logger

log = logger.setup_test_logger()

PRODUCTS_TABLE = 'products-unittest'


class TestHandler:
    def test_fails_due_to_missing_data(self, api_product_update_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        api_product_update_event['body'] = "{\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"price\": \"120.99\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Event body did not contain the retailer.', "response did not contain the correct error message."

    def test_fails_due_to_update_error(self, api_product_update_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', 'badtable-unittest')

        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'No table found', "response did not contain the correct error message."

    def test_update_product(self, api_product_update_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['updated'], "response was not as expected."
