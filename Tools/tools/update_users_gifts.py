import json
import os
import boto3
import uuid
import copy
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        data = {}

        products_table, notfound_table, lists_table = common.get_table_names(os.environ)

        # Step 1: Get the product Id and details from event.
        notfound_id = common.get_path_id(event)
        new_product_details = common.new_product_details(event)

        # Step 2: Create new product item in products table
        # Get the existing product item from notfound table.  Then use the table to prepare object to be added to products table
        notfound_product = notfound_table_get_product(notfound_table, notfound_id)
        products_product = build_products_item(notfound_product, new_product_details)
        products_id = products_table_create_product(products_table, products_product)
        if products_id:
            products_product['productId'] = {'S': products_id}
            add_to_response_data(data, 'products-product-created', products_product, [])
        else:
            add_to_response_data(data, 'products-product-created', [], products_product)

        # Step 3: Update list with new product and reservation items; delete old notfound and reservation items.
        # Get the product and reservation list items. Prepare items to create and delete.
        list_id = get_list_id(lists_table, notfound_id)
        list_query_results = get_all_list_items(lists_table, list_id)
        list_existing_items = find_product_and_reserved_items(list_query_results, notfound_id)
        list_add_items = build_list_product_items(list_existing_items, products_id)

        deletes = delete_notfound_items(lists_table, list_existing_items)
        add_to_response_data(data, 'lists-notfound-deleted', deletes['deleted'], deletes['failed'])

        adds = add_product_items(lists_table, list_add_items)
        add_to_response_data(data, 'lists-products-added', adds['added'], adds['failed'])

        # step 4: Delete notfound item.
        result = notfound_table_delete_product(notfound_table, notfound_id)
        if result:
            add_to_response_data(data, 'notfound-product-deleted', notfound_product, [])
        else:
            add_to_response_data(data, 'notfound-product-deleted', [], notfound_product)

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def add_to_response_data(data, key, succeeded_items, failed_items):
    if len(succeeded_items) > 0:
        data[key + '_succeeded'] = succeeded_items

    if len(failed_items) > 0:
        data[key + '_failed'] = failed_items


def notfound_table_delete_product(notfound_table, id):
    key = {'productId': {'S': id}}
    condition = {':productId': {'S': id}}

    try:
        log.info("Deleting product item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=notfound_table,
            Key=key,
            ConditionExpression="productId = :productId",
            ExpressionAttributeValues=condition
        )
        log.info("Delete response: {}".format(response))
    except Exception as e:
        log.error("Product could not be deleted. Exception: {}".format(e))
        return False

    return True


def notfound_table_get_product(notfound_table, id):
    key = {'productId': {'S': id}}

    try:
        response = dynamodb.get_item(
            TableName=notfound_table,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    log.info("Get product item response: {}".format(response))

    if 'Item' not in response:
        raise Exception("No product returned for the id {}.".format(id))

    return response['Item']


def products_table_create_product(products_table, new_product):
    id = str(uuid.uuid4())
    new_product['productId'] = {'S': id}

    try:
        log.info("Product item to be put in table: {}".format(new_product))
        dynamodb.put_item(TableName=products_table, Item=new_product)
    except Exception as e:
        log.error("Product could not be created: {}".format(e))
        raise Exception('Product could not be created.')

    return id


def add_product_items(lists_table, items):
    adds = {"added": [], "failed": []}

    for item in items:
        try:
            log.info("Put product item: {}".format(item))
            response = dynamodb.put_item(
                TableName=lists_table,
                Item=item,
                ConditionExpression='attribute_not_exists(PK)'
            )
            log.info("Add response: {}".format(response))
            adds['added'].append(item)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                log.error("Product {} already exists in list {}.".format(item['SK']['S'], item['PK']['S']))
            else:
                log.error("Product could not be created: {}".format(e))

            adds['failed'].append(item)

    return adds


def delete_notfound_items(lists_table, items):
    deletes = {"deleted": [], "failed": []}

    for item in items:
        key = {'PK': {'S': item['PK']['S']}, 'SK': {'S': item['SK']['S']}}

        condition = {':PK': {'S': item['PK']['S']}, ':SK': {'S': item['SK']['S']}}

        try:
            log.info("Deleting product item: {}".format(key))
            response = dynamodb.delete_item(
                TableName=lists_table,
                Key=key,
                ConditionExpression="PK = :PK AND SK = :SK",
                ExpressionAttributeValues=condition
            )
            log.info("Delete response: {}".format(response))
            deletes['deleted'].append(item)
        except Exception as e:
            log.error("Product could not be deleted. Exception: {}".format(e))
            deletes['failed'].append(item)

    return deletes


def build_list_product_items(items, products_id):
    product_items = copy.deepcopy(items)

    for item in product_items:
        if "PRODUCT#" in item['SK']['S']:
            item['SK']['S'] = "PRODUCT#" + products_id
            item['type']['S'] = "products"
        elif "RESERVATION#" in item['SK']['S']:
            sk_split = item['SK']['S'].split("#")
            item['SK']['S'] = "RESERVATION#" + products_id + "#" + sk_split[2] + '#' + sk_split[3]
            item['productId']['S'] = products_id
            item['productType']['S'] = 'products'

    return product_items


def find_product_and_reserved_items(items, notfound_id):
    related_items = []

    for item in items:
        log.debug("Checking response item: {}".format(item))
        if item['SK']['S'] == "PRODUCT#" + notfound_id:
            log.info("Adding product item ({})".format(item))
            related_items.append(item)
        elif "RESERVATION#" + notfound_id in item['SK']['S']:
            log.info("Adding reserved item ({})".format(item))
            related_items.append(item)

    return related_items


def get_all_list_items(lists_table, list_id):
    try:
        response = dynamodb.query(
            TableName=lists_table,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        log.info("Response: " + json.dumps(response))
    except ClientError as e:
        raise Exception("Unexpected error when getting list item from table: " + json.dumps(e.response))

    if len(response['Items']) == 0:
        raise Exception("No query results for List ID {}.".format(list_id))

    return response['Items']


def get_list_id(lists_table, notfound_id):
    try:
        response = dynamodb.query(
            TableName=lists_table,
            IndexName='SK-index',
            KeyConditionExpression="SK = :SK",
            ExpressionAttributeValues={":SK":  {'S': "PRODUCT#" + notfound_id}}
        )
        log.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting pending lists from table.")

    if len(response['Items']) == 0:
        raise Exception("No lists for product {} were returned.".format(notfound_id))

    if len(response['Items']) > 1:
        raise Exception("Too many list items for product {} returned [{}].".format(notfound_id, response['Items']))

    return response['Items'][0]['PK']['S'].split("#")[1]


def build_products_item(notfound_product, new_product_details):
    product = {
        "brand": {'S': new_product_details['brand']},
        "details": {'S': new_product_details['details']},
        "retailer": {'S': new_product_details['retailer']},
        "imageUrl": {'S': new_product_details['imageUrl']},
    }

    if 'price' in new_product_details:
        product['price'] = {'S': new_product_details['price']}

    if 'productUrl' in new_product_details:
        product['productUrl'] = {'S': new_product_details['productUrl']}
    else:
        product['productUrl'] = {'S': notfound_product['productUrl']['S']}

    return product
