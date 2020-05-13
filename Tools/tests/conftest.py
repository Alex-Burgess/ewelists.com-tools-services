import json
import os
import pytest
import boto3
from moto import mock_dynamodb2

LISTS_TABLE = 'lists-unittest'
NOTFOUND_TABLE = 'notfound-unittest'
PRODUCTS_TABLE = 'products-unittest'


@pytest.fixture
def dynamodb_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create lists table
        table = dynamodb.create_table(
            TableName='lists-unittest',
            KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'reservationId', 'AttributeType': 'S'},
                {'AttributeName': 'userId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'userId-index',
                    'KeySchema': [{'AttributeName': 'userId', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'SK-index',
                    'KeySchema': [{'AttributeName': 'SK', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'reservationId-index',
                    'KeySchema': [{'AttributeName': 'reservationId', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )

        items = load_test_data(LISTS_TABLE + '.json')

        for item in items:
            table.put_item(TableName='lists-unittest', Item=item)

        # Create notfound table
        table = dynamodb.create_table(
            TableName=NOTFOUND_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(NOTFOUND_TABLE + '.json')

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

        items = load_test_data(PRODUCTS_TABLE + '.json')

        for item in items:
            table.put_item(TableName=PRODUCTS_TABLE, Item=item)
        # End of products

        yield


@pytest.fixture
def empty_notfound_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        dynamodb.create_table(
            TableName=NOTFOUND_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        yield


@pytest.fixture
def notfound_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
            TableName=NOTFOUND_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(NOTFOUND_TABLE + '.json')

        for item in items:
            table.put_item(TableName=NOTFOUND_TABLE, Item=item)

        yield


def load_test_data(name):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../data/' + name)

    items = []
    with open(filename, 'r') as f:
        for row in f:
            items.append(json.loads(row))
    return items


def api_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists",
            "httpMethod": "GET",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570551760227,
            "requestId": "a3d965cd-a79b-4249-867a-a03eb858a839",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": "ABCDEFGPDMJL4EB35H6H",
                "cognitoAuthenticationType": "authenticated",
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl",
                "userArn": "arn:aws:sts::123456789012:assumed-role/Ewelists-test-CognitoAuthRole/CognitoIdentityCredentials",
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials"
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "body": None,
        "isBase64Encoded": "false"
    }


@pytest.fixture
def api_base_event():
    return api_event()


@pytest.fixture
def api_add_product_details_event():
    event = api_event()
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
def api_path_id_event():
    event = api_event()
    event['resource'] = "/tools/products/{id}"
    event['path'] = "/tools/products/12345678-notf-0001-1234-abcdefghijkl"
    event['pathParameters'] = {"id": "12345678-notf-0001-1234-abcdefghijkl"}
    return event


@pytest.fixture
def api_no_path_id_event():
    event = api_event()
    event['resource'] = "/tools/products/"
    event['path'] = "/tools/products/"
    return event


@pytest.fixture
def api_product_body_event():
    event = api_event()
    event['body'] = "{\n    \"brand\": \"Brand1\",\n    \"details\": \"A travel cot, black\",\n    \"retailer\": \"Bigshop\",\n    \"imageUrl\": \"https://example.com/images/product1.jpg\"\n}"
    return event


@pytest.fixture
def scheduled_event():
    return {
        "version": "0",
        "id": "6c57735b-f38d-d066-7141-2c63f06ac1da",
        "detail-type": "Scheduled Event",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2020-05-13T10:00:00Z",
        "region": "eu-west-1",
        "resources": [
            "arn:aws:events:eu-west-1:123456789012:rule/Service-Tools-test-NotFoundCheckFunctionCheckItems-6MQ9JRTJ8RT9"
        ],
        "detail": {}
    }
