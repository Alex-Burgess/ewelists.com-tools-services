import os
import json
from tools import notfound_count, logger

log = logger.setup_test_logger()

NOTFOUND_TABLE = 'notfound-unit'


class TestHandler:
    def test_notfound_empty(self, api_notfound_count_event, monkeypatch, empty_notfound_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)

        response = notfound_count.handler(api_notfound_count_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['count'] == 0, "Number of items was not as expected."

    def test_notfound_has_items(self, api_notfound_count_event, monkeypatch, notfound_mock):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)

        response = notfound_count.handler(api_notfound_count_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['count'] == 2, "Number of items was not as expected."
