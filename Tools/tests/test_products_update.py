import os
import json
import pytest
import mock
import boto3
from tools import products_update, logger

log = logger.setup_test_logger()

PRODUCTS_TEST_TABLE = 'products-test-unit'
PRODUCTS_STAGING_TABLE = 'products-staging-unit'
PRODUCTS_PROD_TABLE = 'products-prod-unit'


@pytest.fixture
def environments(monkeypatch):
    monkeypatch.setitem(os.environ, 'PRODUCTS_TEST_TABLE_NAME', PRODUCTS_TEST_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_STAGING_TABLE_NAME', PRODUCTS_STAGING_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_PROD_TABLE_NAME', PRODUCTS_PROD_TABLE)
    monkeypatch.setitem(os.environ, 'ACCOUNT_ID_TEST', '111111111111')
    monkeypatch.setitem(os.environ, 'ACCOUNT_ID_STAGING', '222222222222')
    monkeypatch.setitem(os.environ, 'ACCOUNT_ID_PROD', '33333333333')
    monkeypatch.setitem(os.environ, 'ENVIRONMENT', 'test')
    monkeypatch.setitem(os.environ, 'CROSS_ACCOUNT_ROLE', 'Cross-Account-Assume-Role')

    return monkeypatch


@pytest.fixture
def tables():
    return {
        'test': 'products-test-unit',
        'staging': 'products-staging-unit',
        'prod': 'products-prod-unit'
    }


@pytest.fixture
def product():
    return {
            "productId": "12345678-prod-0010-1234-abcdefghijkl",
            "brand": "John Lewis & Partners",
            "retailer": "johnlewis.com",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "price": "9.00",
            "priceCheckedDate": "2020-08-27 16:00:00",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
        }


@mock.patch("tools.common.get_dynamodb_client", mock.MagicMock(return_value=boto3.client('dynamodb')))
class TestHandler:
    def test_fails_due_to_missing_data(self, api_product_update_event, environments, products_all_environments):
        api_product_update_event['body'] = json.dumps({
            "brand": "John Lewis & Partners",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "price": "100.00",
            "test": True,
            "staging": True,
            "prod": True
        })

        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Event body did not contain the retailer.', "response did not contain the correct error message."

    def test_fails_due_to_update_error(self, api_product_update_event, environments, products_all_environments, monkeypatch):
        monkeypatch.setitem(os.environ, 'PRODUCTS_STAGING_TABLE_NAME', 'badtable-test')

        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            'test': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'staging': 'Failed: Unexpected error when updating',
            'prod': 'Updated: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."

    def test_update_product(self, api_product_update_event, environments, products_all_environments):
        response = products_update.handler(api_product_update_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            'test': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'staging': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'prod': 'Updated: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."


@mock.patch("tools.common.get_dynamodb_client", mock.MagicMock(return_value=boto3.client('dynamodb')))
class TestMakeChanges:
    def test_updates_to_all_environments(self, products_all_environments, tables, accounts, product):
        environments_to_update = ['test', 'staging', 'prod']
        id = "12345678-prod-0010-1234-abcdefghijkl"
        product['price'] = '100.00'

        error, results = products_update.make_changes(tables, accounts, 'Cross-Account-Assume-Role', 'test', environments_to_update, id, product)
        assert not error, "No error was expected."
        assert results == {
            'test': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'staging': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'prod': 'Updated: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."

    def test_create_missing_product_in_test(self, products_all_envs_with_bad_data, tables, accounts, product):
        environments_to_update = ['test', 'staging', 'prod']
        id = "12345678-prod-0010-1234-abcdefghijkl"
        product['price'] = '100.00'

        error, results = products_update.make_changes(tables, accounts, 'Cross-Account-Assume-Role', 'test', environments_to_update, id, product)
        assert not error, "No error was expected."
        assert results == {
            'test': 'Created: 12345678-prod-0010-1234-abcdefghijkl',
            'staging': 'Updated: 12345678-prod-0010-1234-abcdefghijkl',
            'prod': 'Updated: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."

    def test_update_only_test(self, products_all_envs_with_bad_data, tables, accounts, product):
        environments_to_update = ['test']
        id = "12345678-prod-0010-1234-abcdefghijkl"

        error, results = products_update.make_changes(tables, accounts, 'Cross-Account-Assume-Role', 'test', environments_to_update, id, product)
        assert not error, "No error was expected."
        assert results == {
            'test': 'Created: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."

    def test_updates_failed(self, products_all_environments, tables, accounts, product):
        tables = {
            'test': 'products-test-unit-bad',
            'staging': 'products-staging-unit-bad',
            'prod': 'products-prod-unit'
        }
        environments_to_update = ['test', 'staging', 'prod']
        id = "12345678-prod-0010-1234-abcdefghijkl"
        product['price'] = '100.00'

        error, results = products_update.make_changes(tables, accounts, 'Cross-Account-Assume-Role', 'test', environments_to_update, id, product)
        assert error, "An error was expected."
        assert results == {
            'test': 'Failed: Unexpected error when updating',
            'staging': 'Failed: Unexpected error when updating',
            'prod': 'Updated: 12345678-prod-0010-1234-abcdefghijkl'
        }, "Results object was not as expected."
