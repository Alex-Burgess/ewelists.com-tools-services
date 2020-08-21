import os
import json
from tools import notfound_list, logger

log = logger.setup_test_logger()

NOTFOUND_TABLE = 'notfound-unittest'


class TestHandler:
    def test_notfound_empty(self, api_notfound_list_event, monkeypatch, empty_notfound_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)

        response = notfound_list.handler(api_notfound_list_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert len(body['items']) == 0, "Number of items was not as expected."

    def test_notfound_has_items(self, api_notfound_list_event, monkeypatch, notfound_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)

        response = notfound_list.handler(api_notfound_list_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert len(body['items']) == 2, "Number of items was not as expected."
        assert body['items'][0] == {
            "productId": "12345678-notf-0010-1234-abcdefghijkl",
            "createdBy": "12345678-user-0001-1234-abcdefghijkl",
            "brand": "JL",
            "details": "Safari Mobile",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"
        }, "Product item was not as expected"

        assert body['items'][1] == {
            "productId": "12345678-notf-0011-1234-abcdefghijkl",
            "createdBy": "12345678-user-0001-1234-abcdefghijkl",
            "brand": "Tommee Tippee",
            "details": "Feeding Set",
            "productUrl": "https://www.johnlewis.com/tommee-tippee-closer-to-nature-complete-feeding-set-white/p4159158"
        }, "Product item was not as expected"
