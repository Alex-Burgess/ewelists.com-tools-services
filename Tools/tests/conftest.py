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
def api_update_users_gifts_event_2():
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
        "price": "20.99",
        "searchHidden": True
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
def api_products_get_event_2():
    event = api_event()
    event['resource'] = "/tools/products/{id}"
    event['path'] = "/tools/products/12345678-prod-0011-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0011-1234-abcdefghijkl"}

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
        "searchHidden": False,
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
def api_product_body_event_2():
    event = api_event()
    event['body'] = json.dumps({
        "brand": "Brand1",
        "details": "A travel cot, black",
        "retailer": "bigshop.com",
        "imageUrl": "https://example.com/images/product1.jpg",
        "productUrl": "https://example.com/product123456",
        "price": "19.99",
        "searchHidden": True
    })
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
def api_query_metadata_event():
    event = api_event()
    event['resource'] = "/tools/query/metadata/{url}"
    event['path'] = "/tools/query/metadata/https%3A%2F%2Fwww.thewhitecompany.com%2Fuk%2FSnowman-Knitted-Romper%2Fp%2FSNTOO"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"url": "https%3A%2F%2Fwww.thewhitecompany.com%2Fuk%2FSnowman-Knitted-Romper%2Fp%2FSNTOO"}

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


@pytest.fixture
def metadata_response_wc():
    return {
      "og": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
        "image:width": "200",
        "image:height": "200",
        "url": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
        "type": "product",
        "locale": "en_GB",
        "site_name": "The  White Company UK"
      },
      "meta": {
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "product:price:amount": "34.0",
        "product:price:currency": "GBP",
        "": [
          "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
          "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
          "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
          "200",
          "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
          "product",
          "en_GB",
          "The  White Company UK",
          "1851456161814830"
        ]
      },
      "dc": {},
      "page": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company UK",
        "canonical": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO"
      }
    }


@pytest.fixture
def metadata_response_jl():
    return {
      'og': {},
      'meta': {
        'description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:image': 'https://johnlewis.scene7.com/is/image/JohnLewis/235862595?',
        'og:type': 'product',
        'og:title': 'Mini Micro Deluxe Scooter, 2-5 years, Aqua',
        'og:locale': 'en_GB',
        'og:image:type': 'image/jpeg',
        'og:url': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/aqua/p3567221',
        'og:description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:site-name': 'John Lewis'
      },
      'dc': {},
      'page': {
        'title': 'Mini Micro Deluxe Scooter, 2-5 years at John Lewis & Partners',
        'canonical': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/p3567221'
      }
    }


@pytest.fixture
def metadata_response_jojo():
    return {
      'og': {
        'type': 'product',
        'title': "Kids' Penguin Towelling Dressing Gown",
        'image': 'https://www.jojomamanbebe.co.uk/media/catalog/product/cache/e8cfbc35dc14c111e189893c9b8f265c/h/1/h1182_e2883.jpg',
        'description': '',
        'url': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html'
        },
      'meta': {
        'title': "Kids' Penguin Towelling Bath Robe | JoJo Maman Bebe",
        'description': "The Penguin Towelling Dressing Gown is an impossibly cute style that's both practical and fun to wear. Supersoft cotton terry is so cosy, making it useful for chilly mornings and nights. The hooded style makes it extra warm, and little ones will love the", 'keywords': 'JoJo Maman Bebe',
        'og:type': 'product',
        'og:title': "Kids' Penguin Towelling Dressing Gown",
        'og:image': 'https://www.jojomamanbebe.co.uk/media/catalog/product/cache/e8cfbc35dc14c111e189893c9b8f265c/h/1/h1182_e2883.jpg',
        'og:description': '',
        'og:url': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html',
        'product:price:amount': '18',
        'product:price:currency': 'GBP',
      },
      'dc': {},
      'page': {
        'title': "Kids' Penguin Towelling Bath Robe | JoJo Maman Bebe",
        'canonical': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html'
      }
    }


@pytest.fixture
def metadata_response_gltc():
    return {
      'og': {
        'site_name': 'Great Little Trading Co.',
        'url': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar',
        'title': 'Woodland Christmas Advent Calendar',
        'type': 'product',
        'description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.",
        'price:amount': '45.00',
        'price:currency': 'GBP',
        'image': [
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ],
        'image:secure_url': [
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ]
      },
      'meta': {
        'description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.", 'og:site_name': 'Great Little Trading Co.',
        'og:url': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar',
        'og:title': 'Woodland Christmas Advent Calendar',
        'og:type': 'product',
        'og:description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.",
        'og:price:amount': '45.00',
        'og:price:currency': 'GBP',
        'og:image': [
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ],
        'og:image:secure_url': [
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ]
      },
      'dc': {},
      'page': {
        'title': "Kids' Christmas Advent Calendar | Great Little Trading Co.",
        'canonical': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar'
      }
    }


@pytest.fixture
def metadata_response_sb():
    return {
      'og': {
        'url': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse',
        'site_name': 'Scandibørn',
        'type': 'product',
        'title': 'Plum Play Discovery Woodland Treehouse',
        'image': [
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'image:secure_url': [
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'price:amount': '399.95',
        'price:currency': 'GBP',
        'description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.'
      },
      'meta': {
        'description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.',
        'author': 'Scandibørn',
        'og:url': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse',
        'og:site_name': 'Scandibørn',
        'og:type': 'product',
        'og:title': 'Plum Play Discovery Woodland Treehouse',
        'og:image': [
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'og:image:secure_url': [
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'og:price:amount': '399.95',
        'og:price:currency': 'GBP',
        'og:description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.',
      },
      'dc': {},
      'page': {
        'title': 'Plum Play Discovery Woodland Treehouse | Scandiborn',
        'canonical': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse'
      }
    }


@pytest.fixture
def metadata_response_mp():
    return {
      'og': {
        'url': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2',
        'site_name': 'Mamas & Papas',
        'title': 'Santa Christmas Jumper',
        'type': 'product',
        'description': 'Get ready for cosy Christmas cuddles. Our Christmas 2020 range is filled with festive fun for your little one, with cute winter characters and merry prints.',
        'image': 'https://media.mamasandpapas.com/i/mamasandpapas/S22LXY2_HERO_SANTA XMAS JUMPER'
      },
      'meta': {
        'og:url': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2',
        'og:site_name': 'Mamas & Papas',
        'og:title': 'Santa Christmas Jumper',
        'og:type': 'product',
        'og:description': 'Get ready for cosy Christmas cuddles. Our Christmas 2020 range is filled with festive fun for your little one, with cute winter characters and merry prints.',
        'og:image': 'https://media.mamasandpapas.com/i/mamasandpapas/S22LXY2_HERO_SANTA XMAS JUMPER',
        'product:price:amount': '14.25',
        'product:price:currency': 'GBP'
      },
      'dc': {},
      'page': {
        'title': 'Santa Christmas Jumper | Mamas & Papas',
        'canonical': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2'
      }
    }


@pytest.fixture
def metadata_response_k():
    return {
      'og': {},
      'meta': {
        'og:site_name': 'KIDLY',
        'description': 'The KIDLY Label Recycled Gilet - A go-to warm layer with cool eco creds, to wear under rainwear or over hoodies, in colours to love.',
        'og:title': 'Buy the KIDLY Label Recycled Gilet at KIDLY UK',
        'og:url': '/products/kidly/recycled-gilet/9993',
        'og:type': 'product',
        'og:description': 'The KIDLY Label Recycled Gilet - A go-to warm layer with cool eco creds, to wear under rainwear or over hoodies, in colours to love.',
        'og:image': 'https://kidlycatalogue.blob.core.windows.net/products/9993/product-images/brown-toffee-1/kidly-puffa-gilet-brown-toffee-500x500_02.jpg',
        'og:image:type': 'image/jpeg',
        'og:image:width': '500',
        'og:image:height': '500'
      },
      'dc': {},
      'page': {
        'title': 'Buy the KIDLY Label Recycled Gilet at KIDLY UK',
        'canonical': 'https://www.kidly.co.uk/products/kidly/recycled-gilet/9993'
      }
    }
