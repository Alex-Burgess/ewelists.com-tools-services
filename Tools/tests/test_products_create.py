import pytest
import os
import json
import mock
from tools import products_create, logger

log = logger.setup_test_logger()

PRODUCTS_TABLE = 'products-unittest'


class TestHandler:
    def test_fails_due_to_missing_data(self, api_product_create_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        api_product_create_event['body'] = "{\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"price\": \"120.99\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Event body did not contain the retailer.', "response did not contain the correct error message."

    def test_fails_due_to_put_error(self, api_product_create_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', 'badtable-unittest')

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'Product could not be created.', "response did not contain the correct error message."

    def test_create_product(self, api_product_create_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert len(body['productId']) == 36, "response did not contain a product ID."


class TestGetProductInfo:
    @mock.patch("tools.common.currentTimestamp", mock.MagicMock(return_value="2020-08-27 16:00:00"))
    def test_get_product_info(self):

        body_object = {
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99"
        }

        product = products_create.product_details(body_object)
        assert len(product['productId']['S']) == 36, "Attribute was not as expected."
        assert product['retailer']['S'] == "amazon", "Attribute was not as expected."
        assert product['brand']['S'] == "BABYBJÖRN", "Attribute was not as expected."
        assert product['details']['S'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute was not as expected."
        assert product['price']['S'] == "120.99", "Attribute was not as expected."
        assert product['priceCheckedDate']['S'] == "2020-08-27 16:00:00", "Attribute was not as expected."
        assert product['productUrl']['S'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute was not as expected."
        assert product['imageUrl']['S'] == "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg", "Attribute was not as expected."

    def test_with_empty_body_throws_exception(self):
        body_object = {
            "brand": "John Lewis"
        }

        with pytest.raises(Exception) as e:
            products_create.product_details(body_object)
        assert str(e.value) == "API Event body did not contain correct attributes.", "Exception not as expected."
