import pytest
import os
import json
from tools import common, logger

log = logger.setup_test_logger()


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetEnvironmentVariable:
    def test_get_variable(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        assert table_name == "lists-test", "Table name from os environment variables was not as expected."

    def test_get_with_variable_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_env_variable(os.environ, 'TABLE_NAME')
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetProductDetails:
    def test_new_product_details(self, api_product_body_event):
        product = common.new_product_details(api_product_body_event)
        expected_product = {
            "brand": "Brand1",
            "details": "A travel cot, black",
            "retailer": "bigshop.com",
            "imageUrl": "https://example.com/images/product1.jpg",
            "productUrl": "https://example.com/product123456",
            "price": "19.99"
        }
        assert product == expected_product, "Product details were not as expected."

    def test_no_brand_in_body(self, api_product_body_event):
        api_product_body_event['body'] = "{\n    \"details\": \"A travel cot, black\",\n    \"retailer\": \"bigshop.com\",\n    \"imageUrl\": \"https://example.com/images/product1.jpg\"\n}"
        with pytest.raises(Exception) as e:
            common.new_product_details(api_product_body_event)
        assert str(e.value) == "API Event body did not contain the brand.", "Exception not as expected."

    def test_no_details_in_body(self, api_product_body_event):
        api_product_body_event['body'] = "{\n    \"brand\": \"Brand1\",\n    \"retailer\": \"bigshop.com\",\n    \"imageUrl\": \"https://example.com/images/product1.jpg\"\n}"
        with pytest.raises(Exception) as e:
            common.new_product_details(api_product_body_event)
        assert str(e.value) == "API Event body did not contain the details.", "Exception not as expected."

    def test_no_retailer_in_body(self, api_product_body_event):
        api_product_body_event['body'] = "{\n    \"brand\": \"Brand1\",\n    \"details\": \"A travel cot, black\",\n    \"imageUrl\": \"https://example.com/images/product1.jpg\"\n}"
        with pytest.raises(Exception) as e:
            common.new_product_details(api_product_body_event)
        assert str(e.value) == "API Event body did not contain the retailer.", "Exception not as expected."

    def test_no_imageurl_in_body(self, api_product_body_event):
        api_product_body_event['body'] = "{\n    \"brand\": \"Brand1\",\n    \"details\": \"A travel cot, black\",\n    \"retailer\": \"bigshop.com\"\n}"
        with pytest.raises(Exception) as e:
            common.new_product_details(api_product_body_event)
        assert str(e.value) == "API Event body did not contain the imageUrl.", "Exception not as expected."


class TestGetTableNames:
    def test_get_table_names(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', 'products-test')
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', 'notfound-test')
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', 'lists-test')

        products_table, notfound_table, lists_table = common.get_table_names(os.environ)
        assert products_table == "products-test", "Table name from os environment variables was not as expected."
        assert notfound_table == "notfound-test", "Table name from os environment variables was not as expected."
        assert lists_table == "lists-test", "Table name from os environment variables was not as expected."

    def test_products_name_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', 'notfound-test')
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', 'lists-test')

        with pytest.raises(Exception) as e:
            common.get_table_names(os.environ)
        assert str(e.value) == "Table environment variables not set correctly.", "Exception not as expected."

    def test_notfound_name_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', 'products-test')
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', 'lists-test')

        with pytest.raises(Exception) as e:
            common.get_table_names(os.environ)
        assert str(e.value) == "Table environment variables not set correctly.", "Exception not as expected."

    def test_lists_name_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', 'products-test')
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', 'notfound-test')

        with pytest.raises(Exception) as e:
            common.get_table_names(os.environ)
        assert str(e.value) == "Table environment variables not set correctly.", "Exception not as expected."


class TestGetPathId:
    def test_get_path_id(self, api_path_id_event):
        id = common.get_path_id(api_path_id_event)
        assert id == "12345678-notf-0001-1234-abcdefghijkl", "ID returned from API event was not as expected."

    def test_product_id_not_present(self, api_no_path_id_event):
        with pytest.raises(Exception) as e:
            common.get_path_id(api_no_path_id_event)
        assert str(e.value) == "API Event did not contain a path parameter called ID.", "Exception not as expected."


class TestCheckEnvironments:
    def test_missing_environment_throws_exception(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon.co.uk",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99"
        })

        with pytest.raises(Exception) as e:
            common.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the test attribute.", "Exception not as expected."

        # Staging and Prod missing
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon.co.uk",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True
        })

        with pytest.raises(Exception) as e:
            common.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the staging attribute.", "Exception not as expected."

        # Prod missing
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon.co.uk",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": True
        })

        with pytest.raises(Exception) as e:
            common.check_environments(api_product_create_event)
        assert str(e.value) == "API Event body did not contain the prod attribute.", "Exception not as expected."

    def test_update_test(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon.co.uk",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": False,
            "prod": False
        })

        environments = common.check_environments(api_product_create_event)
        assert environments == ['test'], "Environments array not as expected."

    def test_update_all(self, api_product_create_event):
        api_product_create_event['body'] = json.dumps({
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "retailer": "amazon.co.uk",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "120.99",
            "test": True,
            "staging": True,
            "prod": True
        })

        environments = common.check_environments(api_product_create_event)
        assert environments == ['test', 'staging', 'prod'], "Environments array not as expected."


class TestCrossAccountRoleRequired:
    def test_not_required(self):
        assert not common.cross_account_role_required('products-test-unit', 'test')
        assert not common.cross_account_role_required('products-staging-unit', 'staging')
        assert not common.cross_account_role_required('products-prod-unit', 'prod')

    def test_required(self):
        assert common.cross_account_role_required('products-test-unit', 'staging')
        assert common.cross_account_role_required('products-test-unit', 'prod')
        assert common.cross_account_role_required('products-staging-unit', 'test')
        assert common.cross_account_role_required('products-staging-unit', 'test')
        assert common.cross_account_role_required('products-prod-unit', 'test')
        assert common.cross_account_role_required('products-prod-unit', 'staging')
