import os
import json
from tools import products_get, logger

log = logger.setup_test_logger()

PRODUCTS_TABLE = 'products-unit'


class TestHandler:
    def test_product_missing(self, api_products_get_event, monkeypatch, empty_products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        api_products_get_event['pathParameters']['id'] = "12345678-prod-miss-1234-abcdefghijkl"

        response = products_get.handler(api_products_get_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'No product exists with id: 12345678-prod-miss-1234-abcdefghijkl', "response did not contain the correct error message."

    def test_product_exists(self, api_products_get_event, monkeypatch, products_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)

        response = products_get.handler(api_products_get_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "productId": "12345678-prod-0010-1234-abcdefghijkl",
            "brand": "John Lewis & Partners",
            "retailer": "johnlewis.com",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "price": "9.00",
            "priceCheckedDate": "2020-08-27 16:00:00",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
        }, "Product object not correct."
