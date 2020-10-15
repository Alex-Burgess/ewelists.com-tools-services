import pytest
import os
import json
from tools import products_check_all, logger

log = logger.setup_test_logger()

PRODUCTS_TEST_TABLE = 'products-test-unittest'
PRODUCTS_STAGING_TABLE = 'products-staging-unittest'
PRODUCTS_PROD_TABLE = 'products-prod-unittest'


@pytest.fixture
def environments(monkeypatch):
    monkeypatch.setitem(os.environ, 'PRODUCTS_TEST_TABLE_NAME', PRODUCTS_TEST_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_STAGING_TABLE_NAME', PRODUCTS_STAGING_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_PROD_TABLE_NAME', PRODUCTS_PROD_TABLE)
    monkeypatch.setitem(os.environ, 'PRIMARY_ENVIRONMENT', 'prod')
    monkeypatch.setitem(os.environ, 'UPDATE_ENVIRONMENTS', 'test,staging')
    monkeypatch.setitem(os.environ, 'ENVIRONMENT', 'unittest')

    return monkeypatch


@pytest.fixture
def tables():
    return {
        'test': 'products-test-unittest',
        'staging': 'products-staging-unittest'
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


class TestHandler:
    def test_create_product_all_environments(self, api_product_check_all_event, environments, products_all_environments):
        response = products_check_all.handler(api_product_check_all_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "product": {
                "productId": "12345678-prod-0010-1234-abcdefghijkl",
                "brand": "John Lewis & Partners",
                "retailer": "johnlewis.com",
                "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
                "price": "9.00",
                "priceCheckedDate": "2020-08-27 16:00:00",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
                "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
            },
            "test_environment_states": {
                "staging": "IN SYNC",
                "test": "IN SYNC"
            }
        }, "Response object not correct."

    def test_with_staging_primary(self, api_product_check_all_event, environments, products_all_environments, monkeypatch):
        monkeypatch.setitem(os.environ, 'PRIMARY_ENVIRONMENT', 'staging')
        monkeypatch.setitem(os.environ, 'UPDATE_ENVIRONMENTS', 'test')

        response = products_check_all.handler(api_product_check_all_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "product": {
                "productId": "12345678-prod-0010-1234-abcdefghijkl",
                "brand": "John Lewis & Partners",
                "retailer": "johnlewis.com",
                "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
                "price": "9.00",
                "priceCheckedDate": "2020-08-27 16:00:00",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
                "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
            },
            "test_environment_states": {
                "test": "IN SYNC"
            }
        }, "Response object not correct."

    def test_with_not_in_sync(self, api_product_check_all_event, environments, products_all_envs_with_bad_data):
        response = products_check_all.handler(api_product_check_all_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "product": {
                "productId": "12345678-prod-0010-1234-abcdefghijkl",
                "brand": "John Lewis & Partners",
                "retailer": "johnlewis.com",
                "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
                "price": "9.00",
                "priceCheckedDate": "2020-08-27 16:00:00",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
                "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
            },
            "test_environment_states": {
                "staging": "NOT IN SYNC",
                "test": "DOES NOT EXIST"
            }
        }, "Response object not correct."


class TestSplitTables:
    def test_split_tables(self):
        primary_env = 'prod'
        update_envs = 'test,staging'

        tables = {
            'test': 'products-test-unittest',
            'staging': 'products-staging-unittest',
            'prod': 'products-prod-unittest'
        }

        primary_table, secondary_tables = products_check_all.split_tables(tables, primary_env, update_envs)
        assert primary_table == 'products-prod-unittest'
        assert secondary_tables == {
            'test': 'products-test-unittest',
            'staging': 'products-staging-unittest'
        }

    def test_split_with_staging_primary(self):
        primary_env = 'staging'
        update_envs = 'test'

        tables = {
            'test': 'products-test-unittest',
            'staging': 'products-staging-unittest',
            'prod': 'products-prod-unittest'
        }

        primary_table, secondary_tables = products_check_all.split_tables(tables, primary_env, update_envs)
        assert primary_table == 'products-staging-unittest'
        assert secondary_tables == {
            'test': 'products-test-unittest'
        }


class TestCheckEnvironments:
    def test_check_all_environments_in_sync(self, products_all_environments, tables, product):
        results = products_check_all.check_environments(tables, product, 'unittest')

        assert results == {
            "staging": "IN SYNC",
            "test": "IN SYNC"
        }, "Results were not as expected"

    def test_product_not_in_sync(self, products_all_environments, tables, product):
        product['price'] = "100.00"

        results = products_check_all.check_environments(tables, product, 'unittest')

        assert results == {
            "staging": "NOT IN SYNC",
            "test": "NOT IN SYNC"
        }, "Results were not as expected"

    def test_product_does_not_exist(self, products_all_environments, tables, product):
        product['productId'] = "12345678-prod-1111-1234-abcdefghijkl"

        results = products_check_all.check_environments(tables, product, 'unittest')

        assert results == {
            "staging": "DOES NOT EXIST",
            "test": "DOES NOT EXIST"
        }, "Results were not as expected"

    def test_table_get_item_error(self, products_all_environments, product):
        tables = {'test': 'products-test-unittest-bad'}

        with pytest.raises(Exception) as e:
            products_check_all.check_environments(tables, product, 'unittest')
        assert str(e.value) == "Unexpected problem getting product from table.", "Exception not as expected."
