import pytest
import os
import sys
import json
import logging
import boto3
from moto import mock_dynamodb2
from tools import add_product_details
from tests import fixtures

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

LISTS_TABLE = 'lists-unittest'
NOTFOUND_TABLE = 'notfound-unittest'
PRODUCTS_TABLE = 'products-unittest'


@pytest.fixture
def api_add_product_details_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/tools/products/{id}"
    event['path'] = "/tools/products/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}
    event['body'] = "{\n    \"brand\": \"John Lewis\",\n    \"details\": \"John Lewis & Partners Safari Mobile\", \n    \"retailer\": \"John Lewis\",\n    \"imageUrl\": \"https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$\"\n}"

    return event


@pytest.fixture
def get_all_lists_response():
    return [
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-notf-0010-1234-abcdefghijkl"}, "quantity": {"N": "4"}, "reserved": {"N": "3"}, "type": {"S": "notfound"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reserved": {"N": "1"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reserved": {"N": "0"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "productId": {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reservedAt": {"S": "1573739584"}, "state": {"S": "reserved"}},
        {"PK": {"S": "RESERVATION#12345678-resv-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVATION#12345678-resv-0001-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "email": {"S": "test.user2@gmail.com"}, "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"}, "title": {"S": "Child User1 1st Birthday"}, "productId": {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "productType": {"S": "notfound"}, "quantity": {"N": "2"}, "state": {"S": "reserved"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0002-1234-abcdefghijkl"}, "name": {"S": "Test User3"}, "productId": {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0003-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"S": "1573739584"}, "state": {"S": "reserved"}},
        {"PK":  {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK":  {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"}, "reservationId":  {"S": "12345678-resv-0001-1234-abcdefghijkl"}, "listId":  {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle":  {"S": "Child User1 1st Birthday"}, "name":  {"S": "Test User2"}, "email":  {"S": "test.user2@gmail.com"}, "productId":  {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "productType":  {"S": "products"}, "userId":  {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity":  {"N": "1"}, "reservedAt":  {"N": "1573739584"}, "state":  {"S": "reserved"}},
        {"PK":  {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK":  {"S": "RESERVATION#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl"}, "reservationId":  {"S": "12345678-resv-0002-1234-abcdefghijkl"}, "listId":  {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle":  {"S": "Child User1 1st Birthday"}, "name":  {"S": "Test User2"}, "email":  {"S": "test.user2@gmail.com"}, "productId":  {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "productType":  {"S": "notfound"}, "userId":  {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity":  {"N": "1"}, "reservedAt":  {"N": "1573739584"}, "state":  {"S": "reserved"}},
        {"PK":  {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK":  {"S": "RESERVATION#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl#12345678-resv-0003-1234-abcdefghijkl"}, "reservationId":  {"S": "12345678-resv-0003-1234-abcdefghijkl"}, "listId":  {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle":  {"S": "Child User1 1st Birthday"}, "name":  {"S": "Test User3"}, "email":  {"S": "test.user3@gmail.com"}, "productId":  {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "productType":  {"S": "notfound"}, "userId":  {"S": "12345678-user-0003-1234-abcdefghijkl"}, "quantity":  {"N": "1"}, "reservedAt":  {"N": "1573739584"}, "state":  {"S": "reserved"}}
    ]


@pytest.fixture
def find_product_and_reserved_items():
    return [
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'PRODUCT#12345678-notf-0010-1234-abcdefghijkl'}, 'quantity': {'N': '4'}, 'reserved': {'N': '3'}, 'type': {'S': 'notfound'}},
        {"PK":  {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK":  {"S": "RESERVATION#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl"}, "reservationId":  {"S": "12345678-resv-0002-1234-abcdefghijkl"}, "listId":  {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle":  {"S": "Child User1 1st Birthday"}, "name":  {"S": "Test User2"}, "email":  {"S": "test.user2@gmail.com"}, "productId":  {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "productType":  {"S": "notfound"}, "userId":  {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity":  {"N": "1"}, "reservedAt":  {"N": "1573739584"}, "state":  {"S": "reserved"}},
        {"PK":  {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK":  {"S": "RESERVATION#12345678-notf-0010-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl#12345678-resv-0003-1234-abcdefghijkl"}, "reservationId":  {"S": "12345678-resv-0003-1234-abcdefghijkl"}, "listId":  {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle":  {"S": "Child User1 1st Birthday"}, "name":  {"S": "Test User3"}, "email":  {"S": "test.user3@gmail.com"}, "productId":  {"S": "12345678-notf-0010-1234-abcdefghijkl"}, "productType":  {"S": "notfound"}, "userId":  {"S": "12345678-user-0003-1234-abcdefghijkl"}, "quantity":  {"N": "1"}, "reservedAt":  {"N": "1573739584"}, "state":  {"S": "reserved"}}
    ]


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    # Create lists table
    table = dynamodb.create_table(
        TableName=LISTS_TABLE,
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
        GlobalSecondaryIndexes=[{
            'IndexName': 'SK-index',
            'KeySchema': [{'AttributeName': 'SK', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        }]
    )

    items = fixtures.load_test_data(LISTS_TABLE + '.json')

    for item in items:
        table.put_item(TableName=LISTS_TABLE, Item=item)
    # End of lists

    # Create notfound table
    table = dynamodb.create_table(
        TableName=NOTFOUND_TABLE,
        KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    items = fixtures.load_test_data(NOTFOUND_TABLE + '.json')

    for item in items:
        table.put_item(TableName=NOTFOUND_TABLE, Item=item)
    # End of notfound

    # Create products table
    table = dynamodb.create_table(
        TableName=PRODUCTS_TABLE,
        KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    items = fixtures.load_test_data(PRODUCTS_TABLE + '.json')

    for item in items:
        table.put_item(TableName=PRODUCTS_TABLE, Item=item)
    # End of products

    yield
    # teardown: stop moto server
    mock.stop()


class TestAddToResponseData:
    def test_add_succeeded(self):
        data = {}
        product_data = [{
            'brand': 'John Lewis & Partners',
            'details': 'Savanna Animal Mobile'
        }]

        add_product_details.add_to_response_data(data, 'products-product-created', product_data, [])
        assert data['products-product-created_succeeded']

    def test_add_failed(self):
        data = {}
        product_data = [{
            'brand': 'John Lewis & Partners',
            'details': 'Savanna Animal Mobile'
        }]

        add_product_details.add_to_response_data(data, 'products-product-created', [], product_data)
        assert data['products-product-created_failed']

class TestDeleteProductFromNotfoundTable:
    def test_delete_product(self, dynamodb_mock):
        id = '12345678-notf-0010-1234-abcdefghijkl'
        result = add_product_details.notfound_table_delete_product(NOTFOUND_TABLE, id)
        assert result, "Delete did not succeed."

    def test_product_does_not_exist(self, dynamodb_mock):
        id = '12345678-notf-1010-1234-abcdefghijkl'
        result = add_product_details.notfound_table_delete_product(NOTFOUND_TABLE, id)
        assert not result, "Delete did not fail."


class TestAddProductItems:
    def test_add_product_items(self, dynamodb_mock, find_product_and_reserved_items):
        list_id = find_product_and_reserved_items[0]['PK']['S']
        id = '12345678-prod-abcd-1234-abcdefghijkl'
        products_items = add_product_details.build_list_product_items(find_product_and_reserved_items, id)
        adds = add_product_details.add_product_items(LISTS_TABLE, products_items)
        assert len(adds['failed']) == 0, "There should be no failed items"
        assert len(adds['added']) == 3, "There should be 3 added items"

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.query(
            TableName=LISTS_TABLE,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': list_id}}
        )

        assert len(test_response['Items']) == 10, "Total Items for the list was not as expected."

        # Check that the correct items were deleted:
        for item in products_items:
            response = dynamodb.query(
                TableName=LISTS_TABLE,
                IndexName='SK-index',
                KeyConditionExpression="SK = :SK",
                ExpressionAttributeValues={":SK": item['SK']}
            )

            assert len(response['Items']) == 1, "Item was not added as expected."


class TestDeleteNotfoundItems:
    def test_delete_notfound_items(self, dynamodb_mock, find_product_and_reserved_items):
        list_id = find_product_and_reserved_items[0]['PK']['S']
        deletes = add_product_details.delete_notfound_items(LISTS_TABLE, find_product_and_reserved_items)
        assert len(deletes['failed']) == 0, "There should be no failed items"
        assert len(deletes['deleted']) == 3, "There should be 3 failed items"

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.query(
            TableName=LISTS_TABLE,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': list_id}}
        )

        assert len(test_response['Items']) == 4, "Total Items for the list was not as expected."

        # Check that the correct items were deleted:
        for item in find_product_and_reserved_items:
            response = dynamodb.query(
                TableName=LISTS_TABLE,
                IndexName='SK-index',
                KeyConditionExpression="SK = :SK",
                ExpressionAttributeValues={":SK": item['SK']}
            )

            assert len(response['Items']) == 0, "Item was not deleted as expected."

    def test_entry_not_exists(self, dynamodb_mock):
        items = [{'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'PRODUCT#12345678-notf-1010-1234-abcdefghijkl'}, 'quantity': {'N': '4'}, 'reserved': {'N': '3'}, 'type': {'S': 'notfound'}}]

        deletes = add_product_details.delete_notfound_items(LISTS_TABLE, items)
        assert len(deletes['failed']) == 1, "There should be 1 failed items"
        assert len(deletes['deleted']) == 0, "There should be 0 failed items"


class TestBuildListProductItems:
    def test_build_list_items(self, find_product_and_reserved_items):
        id = '12345678-prod-abcd-1234-abcdefghijkl'
        products_items = add_product_details.build_list_product_items(find_product_and_reserved_items, id)

        assert len(products_items) == 3, "Number of items returned was not the same as submitted."

        expected_product_item = {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'PRODUCT#12345678-prod-abcd-1234-abcdefghijkl'}, 'quantity': {'N': '4'}, 'reserved': {'N': '3'}, 'type': {'S': 'products'}}
        assert products_items[0]['SK']['S'] != find_product_and_reserved_items[0]['SK']['S'], "Product item SK was not updated as expected."
        assert products_items[0]['SK']['S'] == 'PRODUCT#12345678-prod-abcd-1234-abcdefghijkl', 'Attribute not as expected.'
        assert products_items[0] == expected_product_item, "Product item was not as expected."

        expected_reserved_item_1 = {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'RESERVATION#12345678-prod-abcd-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl'}, 'productId': {'S': '12345678-prod-abcd-1234-abcdefghijkl'}, 'name': {'S': 'Test User2'}, 'email': {'S': 'test.user2@gmail.com'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listTitle': {'S': 'Child User1 1st Birthday'}, 'userId': {'S': '12345678-user-0002-1234-abcdefghijkl'}, 'productType': {'S': 'products'}, 'reservationId': {'S': '12345678-resv-0002-1234-abcdefghijkl'}, 'state': {'S': 'reserved'}, 'quantity': {'N': '1'}, 'reservedAt': {'N': '1573739584'}}
        assert products_items[1]['SK']['S'] != find_product_and_reserved_items[1]['SK']['S'], "Reserved item SK was not updated as expected."
        assert products_items[1]['SK']['S'] == 'RESERVATION#12345678-prod-abcd-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl'
        assert products_items[1]['productId']['S'] != find_product_and_reserved_items[1]['productId']['S'], "Reserved item SK was not updated as expected."
        assert products_items[1]['productId']['S'] == '12345678-prod-abcd-1234-abcdefghijkl'
        assert products_items[1] == expected_reserved_item_1, "Reserved item was not as expected."

        expected_reserved_item_2 = {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'RESERVATION#12345678-prod-abcd-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl#12345678-resv-0003-1234-abcdefghijkl'}, 'productId': {'S': '12345678-prod-abcd-1234-abcdefghijkl'}, 'name': {'S': 'Test User3'}, 'email': {'S': 'test.user3@gmail.com'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listTitle': {'S': 'Child User1 1st Birthday'}, 'userId': {'S': '12345678-user-0003-1234-abcdefghijkl'}, 'productType': {'S': 'products'}, 'reservationId': {'S': '12345678-resv-0003-1234-abcdefghijkl'}, 'state': {'S': 'reserved'}, 'quantity': {'N': '1'}, 'reservedAt': {'N': '1573739584'}}
        assert products_items[2]['SK']['S'] != find_product_and_reserved_items[2]['SK']['S'], "Reserved item SK was not updated as expected."
        assert products_items[2]['SK']['S'] == 'RESERVATION#12345678-prod-abcd-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl#12345678-resv-0003-1234-abcdefghijkl'
        assert products_items[2]['productId']['S'] != find_product_and_reserved_items[1]['productId']['S'], "Reserved item SK was not updated as expected."
        assert products_items[2]['productId']['S'] == '12345678-prod-abcd-1234-abcdefghijkl'
        assert products_items[2] == expected_reserved_item_2, "Reserved item was not as expected."


class TestFindProductAndReservedItems:
    def test_find_product_and_reserved_items(self, get_all_lists_response):
        notfound_id = '12345678-notf-0010-1234-abcdefghijkl'
        items = add_product_details.find_product_and_reserved_items(get_all_lists_response, notfound_id)

        assert len(items) == 3


class TestGetAllListItems:
    def test_get_all_list_items(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = add_product_details.get_all_list_items(LISTS_TABLE, list_id)
        assert len(items) == 7, "Number of items was not as expected."

    def test_list_does_not_exist(self, dynamodb_mock):
        list_id = '12345678-list-0100-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            add_product_details.get_all_list_items(LISTS_TABLE, list_id)
        assert str(e.value) == "No query results for List ID 12345678-list-0100-1234-abcdefghijkl.", "Exception not as expected."


class TestGetListId:
    def test_get_list_id(self, dynamodb_mock):
        id = '12345678-notf-0010-1234-abcdefghijkl'
        list_id = add_product_details.get_list_id(LISTS_TABLE, id)
        assert list_id == '12345678-list-0001-1234-abcdefghijkl'


class TestPutProductInProductsTable:
    def test_put_product_in_products_table(self, dynamodb_mock):
        products_item = {
            "brand": {'S': "John Lewis"},
            "details": {'S': "John Lewis & Partners Safari Mobile"},
            "retailer": {'S': "John Lewis"},
            "imageUrl": {'S': "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$"},
            "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
        }

        id = add_product_details.products_table_create_product(PRODUCTS_TABLE, products_item)
        assert len(id) == 36, "Product ID was not expected length"

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.query(
            TableName=PRODUCTS_TABLE,
            KeyConditionExpression="productId = :productId",
            ExpressionAttributeValues={":productId":  {'S': id}}
        )
        product_item = test_response['Items'][0]
        assert product_item['brand']['S'] == "John Lewis"
        assert product_item['details']['S'] == "John Lewis & Partners Safari Mobile"
        assert product_item['retailer']['S'] == "John Lewis"
        assert product_item['imageUrl']['S'] == "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$"
        assert product_item['productUrl']['S'] == "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"


class TestBuildProductsItem:
    def test_build_item(self):
        notfound_product = {
            "productId": {'S': "12345678-notf-0010-1234-abcdefghijkl"},
            "brand": {'S': "JL"},
            "details": {'S': "Safari Mobile"},
            "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
        }

        new_product_details = {
            "brand": "John Lewis",
            "details": "John Lewis & Partners Safari Mobile",
            "retailer": "John Lewis",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$"
        }

        expected_products_item = {
            "brand": {'S': "John Lewis"},
            "details": {'S': "John Lewis & Partners Safari Mobile"},
            "retailer": {'S': "John Lewis"},
            "imageUrl": {'S': "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$"},
            "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
        }

        item = add_product_details.build_products_item(notfound_product, new_product_details)
        assert item == expected_products_item, "Products item was not as expected."


class TestGetProductFromNotfound:
    def test_get_product(self, dynamodb_mock):
        id = '12345678-notf-0010-1234-abcdefghijkl'
        product = add_product_details.notfound_table_get_product(NOTFOUND_TABLE, id)
        expected_product = {
            "productId": {'S': "12345678-notf-0010-1234-abcdefghijkl"},
            "brand": {'S': "JL"},
            "details": {'S': "Safari Mobile"},
            "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"},
            'createdBy': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}
        }
        assert product == expected_product, "Product was not as expected."

    def test_with_missing_product_id(self, dynamodb_mock):
        id = '12345678-notf-0011-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            add_product_details.notfound_table_get_product(NOTFOUND_TABLE, id)
        assert str(e.value) == "No product returned for the id 12345678-notf-0011-1234-abcdefghijkl.", "Exception not as expected."

    def test_with_bad_table(self, dynamodb_mock):
        id = '12345678-prod-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            add_product_details.notfound_table_get_product('notfound-unittes', id)
        assert str(e.value) == "Unexpected problem getting product from table.", "Exception not as expected."


class TestHandler:
    def test_handler(self, api_add_product_details_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)
        monkeypatch.setitem(os.environ, 'NOTFOUND_TABLE_NAME', NOTFOUND_TABLE)
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', LISTS_TABLE)

        response = add_product_details.handler(api_add_product_details_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        products_added = body['products-product-created_succeeded']
        notfound_deleted = body['notfound-product-deleted_succeeded']
        lists_deleted = body['lists-notfound-deleted_succeeded']
        lists_added = body['lists-products-added_succeeded']

        assert products_added['productId']['S'] == lists_added[0]['SK']['S'].split('#')[1]

        expected_products_item = {"brand": {'S': "John Lewis"}, "details": {'S': "John Lewis & Partners Safari Mobile"}, "retailer": {'S': "John Lewis"}, "imageUrl": {'S': "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$"}, "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}}
        del products_added['productId']
        assert products_added == expected_products_item

        assert notfound_deleted == {"productId": {'S': "12345678-notf-0010-1234-abcdefghijkl"}, "brand": {'S': "JL"}, "details": {'S': "Safari Mobile"}, "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}, 'createdBy': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}}

        assert len(lists_added) == 3
        assert len(lists_deleted) == 3
