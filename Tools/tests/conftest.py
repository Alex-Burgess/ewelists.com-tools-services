import json
import os
import pytest
import boto3
from moto import mock_dynamodb2, mock_ssm

LISTS_TABLE = 'lists-unit'
NOTFOUND_TABLE = 'notfound-unit'
PRODUCTS_TABLE = 'products-unit'


@pytest.fixture
def ssm_mock():
    with mock_ssm():
        path = '/Test/APIKey'
        key = "12345678"

        ssm = boto3.client('ssm')
        ssm.put_parameter(Name=path, Value=key, Type='SecureString')

        yield


@pytest.fixture
def dynamodb_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create lists table
        table = dynamodb.create_table(
            TableName='lists-unit',
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

        items = load_test_data(LISTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName='lists-unit', Item=item)

        # Create notfound table
        table = dynamodb.create_table(
            TableName=NOTFOUND_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(NOTFOUND_TABLE + 'test.json')

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

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

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

        items = load_test_data(NOTFOUND_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName=NOTFOUND_TABLE, Item=item)

        yield


@pytest.fixture
def empty_products_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        dynamodb.create_table(
            TableName=PRODUCTS_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        yield


@pytest.fixture
def products_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
            TableName=PRODUCTS_TABLE,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName=PRODUCTS_TABLE, Item=item)

        yield


@pytest.fixture
def products_all_environments():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create test table
        table = dynamodb.create_table(
            TableName='products-test-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName='products-test-unit', Item=item)

        # Create staging table
        table = dynamodb.create_table(
            TableName='products-staging-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName='products-staging-unit', Item=item)

        # Create prod table
        table = dynamodb.create_table(
            TableName='products-prod-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName='products-prod-unit', Item=item)
        # End of products

        yield


@pytest.fixture
def products_all_envs_with_bad_data():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create test table - empty
        table = dynamodb.create_table(
            TableName='products-test-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        # Create staging table - not in sync
        table = dynamodb.create_table(
            TableName='products-staging-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = [{"productId": "12345678-prod-0010-1234-abcdefghijkl", "brand": "John Lewis & Partners", "retailer": "johnlewis.com", "price": "100.00", "priceCheckedDate": "2020-08-27 16:00:00", "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White", "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352", "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"}]

        for item in items:
            table.put_item(TableName='products-staging-unit', Item=item)

        # Create prod table
        table = dynamodb.create_table(
            TableName='products-prod-unit',
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = load_test_data(PRODUCTS_TABLE + 'test.json')

        for item in items:
            table.put_item(TableName='products-prod-unit', Item=item)
        # End of products

        yield


def load_test_data(name):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../data/' + name)

    items = []
    with open(filename, 'r') as f:
        for row in f:
            items.append(json.loads(row))
    return items


@pytest.fixture
def accounts():
    return {
        "products-test-unit": "111111111111",
        "products-staging-unit": "222222222222",
        "products-prod-unit": "33333333333"
    }


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
def api_notfound_get_event():
    event = api_event()
    event['resource'] = "/tools/notfound/{id}"
    event['path'] = "/tools/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_notfound_count_event():
    event = api_event()
    event['resource'] = "/tools/notfound/count"
    event['path'] = "/tools/products/count"
    event['httpMethod'] = "GET"

    return event


@pytest.fixture
def api_notfound_list_event():
    event = api_event()
    event['resource'] = "/tools/notfound/"
    event['path'] = "/tools/notfound/"
    event['httpMethod'] = "GET"

    return event


@pytest.fixture
def api_update_users_gifts_event():
    event = api_event()
    event['resource'] = "/tools/notfound/{id}"
    event['path'] = "/tools/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}
    event['body'] = json.dumps({
        "brand": "John Lewis",
        "details": "John Lewis & Partners Safari Mobile",
        "retailer": "johnlewis.com",
        "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/237244063?$rsp-pdp-port-640$",
        "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165?tagid=123456",
        "price": "20.99"
    })

    return event


@pytest.fixture
def api_product_create_event():
    event = api_event()
    event['resource'] = "/tools/products"
    event['path'] = "/tools/products"
    event['httpMethod'] = "POST"
    event['body'] = json.dumps({
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

    return event


@pytest.fixture
def api_products_get_event():
    event = api_event()
    event['resource'] = "/tools/products/{id}"
    event['path'] = "/tools/products/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_product_check_all_event():
    event = api_event()
    event['resource'] = "/tools/products/check/{id}"
    event['path'] = "/tools/products/check/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_product_update_event():
    event = api_event()
    event['resource'] = "/tools/products/{id}"
    event['path'] = "/tools/products/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}
    event['body'] = "{\n    \"retailer\": \"amazon.co.uk\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"price\": \"100.00\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"
    event['body'] = json.dumps({
        "brand": "John Lewis & Partners",
        "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
        "retailer": "johnlewis.com",
        "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$",
        "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
        "price": "100.00",
        "test": True,
        "staging": True,
        "prod": True
    })

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
    event['body'] = "{\n    \"brand\": \"Brand1\",\n    \"details\": \"A travel cot, black\",\n    \"retailer\": \"bigshop.com\",\n    \"imageUrl\": \"https://example.com/images/product1.jpg\",\n    \"productUrl\": \"https://example.com/product123456\",\n    \"price\": \"19.99\"\n}"
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


@pytest.fixture
def api_check_details_event():
    event = api_event()
    event['resource'] = "/tools/check/details/{url}"
    event['path'] = "/tools/check/details/https%3A%2F%2Fwww.johnlewis.com%2Fgaia-baby-serena-nursing-rocking-chair-oat%2Fp4797478"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"url": "https%3A%2F%2Fwww.johnlewis.com%2Fgaia-baby-serena-nursing-rocking-chair-oat%2Fp4797478"}
    event['body'] = "null"

    return event


@pytest.fixture
def scraping_hub_response():
    return {
        'query': {
            'id': '1599575579454-9cd66182fe9b087f',
            'domain': 'johnlewis.com',
            'userQuery': {
                'url': 'https://www.johnlewis.com/gaia-baby-serena-nursing-rocking-chair-oat/p4797478',
                'pageType': 'product'
            }
        },
        'webPage': {'inLanguages': [{'code': 'en'}]},
        'product': {
            'name': 'Gaia Baby Serena Nursing Rocking Chair, Oat',
            'description': 'Product code: 32481601\n\nBeautifully contoured with classic styling, the Serena Nursing Rocking Chair from Gaia Baby will add a contemporary feel to any nursery or living space.\n\nErgonomically designed to provide optimum comfort as a nursing/feeding chair, it has an extra lumbar cushion and padded armrests and is generously sized to accommodate a parent and child for bedtime stories as they grow. The softly contoured legs are made from laminated birch-wood veneer using a special technique during the manufacturing process to give extra strength and avoid splintering for a smooth and soothing rocking motion.\n\nIt is finely upholstered with removable and washable armrests in durable woven polyester.',
            'mainImage': 'https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$',
            'images': [
                'https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$',
                'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt2?$rsp-pdp-port-1440$',
                'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt3?$rsp-pdp-port-1440$',
                'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt1?$rsp-pdp-port-1440$'
            ],
            'url': 'https://www.johnlewis.com/gaia-baby-serena-nursing-rocking-chair-oat/p4797478',
            'additionalProperty': [
                {'name': 'assembly required', 'value': 'Partial self-assembly required'},
                {'name': 'brand', 'value': 'Gaia Baby'},
                {'name': 'care instructions', 'value': 'Spot clean, washable armrest covers'},
                {'name': 'cover type', 'value': 'Fixed'},
                {'name': 'dimensions', 'value': 'H81 x W94 x D78cm'},
                {'name': 'filling composition', 'value': 'Polyester'},
                {'name': 'finish', 'value': 'Natural'},
                {'name': 'frame construction', 'value': 'Screwed and dowelled'},
                {'name': 'frame material', 'value': 'Birch plywood'},
                {'name': 'fsc certified', 'value': 'YES'},
                {'name': 'material', 'value': '80% Polyester, 20% Viscose, Legs: Birch plywood'},
                {'name': 'product code', 'value': '32481601'},
                {'name': 'quality', 'value': 'Poor'},
                {'name': 'value', 'value': 'Great'},
                {'name': 'value: poor', 'value': 'Quality: Poor'},
                {'name': 'weight read tooltip information unpackaged weight of the product', 'value': '21.2kg'}
            ],
            'offers': [
                {'price': '399.99', 'currency': '£', 'availability': 'InStock'}
            ],
            'sku': '32481601',
            'brand': 'Gaia Baby',
            'breadcrumbs': [
                {'name': 'Homepage', 'link': 'https://www.johnlewis.com/'},
                {'name': 'Baby & Child', 'link': 'https://www.johnlewis.com/baby-child/c5000010'},
                {'name': 'Nursery Furniture & Furnishings', 'link': 'https://www.johnlewis.com/baby-child/nursery-furniture-furnishings/c6000062'},
                {'name': 'Nursing Chairs', 'link': 'https://www.johnlewis.com/browse/baby-child/nursery-furniture-furnishings/nursing-chairs/_/N-8es'}
            ],
            'probability': 0.98316103,
            'aggregateRating': {'reviewCount': 6}
        }
    }
