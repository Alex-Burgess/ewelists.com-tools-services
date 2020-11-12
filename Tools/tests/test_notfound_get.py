import os
import json
from tools import notfound_get, logger

log = logger.setup_test_logger()

NOTFOUND_TABLE = 'notfound-unit'
LISTS_TABLE = 'lists-unit'


class TestHandler:
    def test_product_missing(self, api_notfound_get_event, monkeypatch, empty_notfound_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', LISTS_TABLE)

        api_notfound_get_event['pathParameters']['id'] = "12345678-notf-miss-1234-abcdefghijkl"

        response = notfound_get.handler(api_notfound_get_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'No product exists with id: 12345678-notf-miss-1234-abcdefghijkl', "response did not contain the correct error message."

    def test_product_exists(self, api_notfound_get_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', LISTS_TABLE)

        response = notfound_get.handler(api_notfound_get_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "productId": "12345678-notf-0010-1234-abcdefghijkl",
            "createdBy": "12345678-user-0001-1234-abcdefghijkl",
            "brand": "JL",
            "details": "Safari Mobile",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165",
            "creatorsName": "Test User1",
            "listTitle": "Child User1 1st Birthday",
            "listId": "12345678-list-0001-1234-abcdefghijkl"
        }, "Product item was not as expected"

    def test_full_product_data(self, api_notfound_get_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', LISTS_TABLE)

        api_notfound_get_event['pathParameters']['id'] = '12345678-notf-0020-1234-abcdefghijkl'

        response = notfound_get.handler(api_notfound_get_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "productId": "12345678-notf-0020-1234-abcdefghijkl",
            "createdBy": "12345678-user-0003-1234-abcdefghijkl",
            "brand": "John Lewis",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$",
            "price": "9.00",
            "creatorsName": "Test User3",
            "listTitle": "Child User3 1st Birthday",
            "listId": "12345678-list-0002-1234-abcdefghijkl"
        }, "Product item was not as expected"
