import pytest
import os
import json
import mock
from tools import products_create, logger

log = logger.setup_test_logger()

PRODUCTS_TEST_TABLE = 'products-test-unittest'
PRODUCTS_STAGING_TABLE = 'products-staging-unittest'
PRODUCTS_PROD_TABLE = 'products-prod-unittest'


@pytest.fixture
def environments(monkeypatch):
    monkeypatch.setitem(os.environ, 'PRODUCTS_TEST_TABLE_NAME', PRODUCTS_TEST_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_STAGING_TABLE_NAME', PRODUCTS_STAGING_TABLE)
    monkeypatch.setitem(os.environ, 'PRODUCTS_PROD_TABLE_NAME', PRODUCTS_PROD_TABLE)

    return monkeypatch


class TestHandler:
    def test_fails_due_to_missing_product_data(self, api_product_create_event, environments, products_create_environments):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": True,
            "prod": True
        })

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Event body did not contain the retailer.', "response did not contain the correct error message."

    def test_fails_due_to_missing_environment(self, api_product_create_event, environments, products_create_environments):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "staging": True,
            "prod": True
        })

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Event body did not contain the test attribute.', "response did not contain the correct error message."

    def test_fails_due_to_put_error(self, api_product_create_event, monkeypatch, products_create_environments):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TEST_TABLE_NAME', PRODUCTS_TEST_TABLE)
        monkeypatch.setitem(os.environ, 'PRODUCTS_STAGING_TABLE_NAME', 'products-mis2-unittest')
        monkeypatch.setitem(os.environ, 'PRODUCTS_PROD_TABLE_NAME', PRODUCTS_PROD_TABLE)

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'There was an error when updating one or more environments.', "response did not contain the correct error message."
        assert body['test'].split(":")[0] == "Success"
        assert len(body['test'].split(":")[1]) == 36
        assert body['staging'] == 'Failed:Product could not be created (products-mis2-unittest).', "Test update was not as expected"

    def test_create_product_all_environments(self, api_product_create_event, environments, products_create_environments):
        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert len(body['productId']) == 36, "response did not contain a product ID."
        assert body['test'].split(":")[0] == "Success"
        assert body['staging'].split(":")[0] == "Success"
        assert body['prod'].split(":")[0] == "Success"

    def test_create_product_just_test(self, api_product_create_event, environments, products_create_environments):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": False,
            "prod": False
        })

        response = products_create.handler(api_product_create_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert len(body['productId']) == 36, "response did not contain a product ID."
        assert body['test'].split(":")[0] == "Success"
        assert 'staging' not in body
        assert 'prod' not in body


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

        product = products_create.product_details(body_object, '12345678-prod-new1-1234-abcdefghijkl')
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
            products_create.product_details(body_object, '12345678-prod-new1-1234-abcdefghijkl')
        assert str(e.value) == "API Event body did not contain correct attributes.", "Exception not as expected."


class TestUpdateTables:
    def test_update_test(self, products_create_environments):
        tables = {
            'test': PRODUCTS_TEST_TABLE,
            'staging': PRODUCTS_STAGING_TABLE,
            'prod': PRODUCTS_PROD_TABLE
        }

        environments_to_update = ['test']

        product = {
            "productId": {'S': "12345678-prod-new1-1234-abcdefghijkl"},
            "brand": {'S': "BABYBJÖRN"},
            "details": {'S': "Travel Cot Easy Go, Anthracite, with transport bag"},
            "retailer": {'S': "amazon"},
            "imageUrl": {'S': "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"},
            "productUrl": {'S': "https://www.amazon.co.uk/dp/B01H24LM58"},
            "price": {'S': "120.99"}
        }

        results, errors = products_create.update_tables(tables, environments_to_update, product)
        assert results['test'].split(":")[0] == "Success"
        assert len(results['test'].split(":")[1]) == 36
        assert not errors, "Errors boolean should be false"

    def test_update_to_staging_failed(self, products_create_environments):
        tables = {
            'test': PRODUCTS_TEST_TABLE,
            'staging': 'bad_staging_table',
            'prod': PRODUCTS_PROD_TABLE
        }

        environments_to_update = ['test', 'staging']

        product = {
            "productId": {'S': "12345678-prod-new1-1234-abcdefghijkl"},
            "brand": {'S': "BABYBJÖRN"},
            "details": {'S': "Travel Cot Easy Go, Anthracite, with transport bag"},
            "retailer": {'S': "amazon"},
            "imageUrl": {'S': "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"},
            "productUrl": {'S': "https://www.amazon.co.uk/dp/B01H24LM58"},
            "price": {'S': "120.99"}
        }

        results, errors = products_create.update_tables(tables, environments_to_update, product)
        assert errors, "Errors boolean was not true"

        assert results['test'].split(":")[0] == "Success"
        assert len(results['test'].split(":")[1]) == 36

        assert results['staging'].split(":")[0] == "Failed"
        assert results['staging'].split(":")[1] == "Product could not be created (bad_staging_table)."


class TestCheckEnvironments:
    def test_missing_environment_throws_exception(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99"
        })

        with pytest.raises(Exception) as e:
            products_create.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the test attribute.", "Exception not as expected."

        # Staging and Prod missing
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True
        })

        with pytest.raises(Exception) as e:
            products_create.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the staging attribute.", "Exception not as expected."

        # Prod missing
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": True
        })

        with pytest.raises(Exception) as e:
            products_create.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the prod attribute.", "Exception not as expected."

    def test_update_test(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": False,
            "prod": False
        })

        environments = products_create.check_environments(api_product_create_event)
        assert environments == ['test'], "Environments array not as expected."

    def test_update_all(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": True,
            "prod": True
        })

        environments = products_create.check_environments(api_product_create_event)
        assert environments == ['test', 'staging', 'prod'], "Environments array not as expected."
