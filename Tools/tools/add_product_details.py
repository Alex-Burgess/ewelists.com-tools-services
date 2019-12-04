import json
import os
import boto3
import logging
import uuid
import copy
from tools import common
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        data = {}

        products_table, notfound_table, lists_table = common.get_table_names(os.environ)

        # Step 1: Get the product Id that we will migrating from notfound to products table
        notfound_id = common.get_path_id(event)

        # Step 2: Get the product details from the api event body.
        new_product_details = common.new_product_details(event)

        # Step 3: Get the existing product item from notfound table, which we will take some data from, e.g. productUrl.
        notfound_product = get_product_from_notfound(notfound_table, notfound_id)

        # Step 4: Create product in products table
        products_product = build_products_item(notfound_product, new_product_details)
        products_id = put_product_in_products_table(products_table, products_product)
        if products_id:
            products_product['productId'] = {'S': products_id}
            data['products_added'] = products_product
        else:
            data['products_failed'] = products_product

        # Step 5: Get the product and reserved items
        list_id = get_list_id(lists_table, notfound_id)
        list_query_results = get_all_list_items(lists_table, list_id)
        list_notfound_items = find_product_and_reserved_items(list_query_results, notfound_id)

        # Step 6: Update lists table, removing notfound items and adding products items
        list_product_items = build_list_product_items(list_notfound_items, products_id)
        deletes = delete_notfound_items(lists_table, list_notfound_items)
        if deletes['failed']:
            data['lists_notfound_deleted'] = deletes['deleted']
            data['lists_notfound_failed'] = deletes['failed']
        else:
            data['lists_notfound_deleted'] = deletes['deleted']

        adds = add_product_items(lists_table, list_product_items)
        if adds['failed']:
            data['lists_products_added'] = adds['added']
            data['lists_products_failed'] = adds['failed']
        else:
            data['lists_products_added'] = adds['added']

        # step 7: Delete notfound item.
        result = delete_product_from_notfound_table(notfound_table, notfound_id)
        if result:
            data['notfound_deleted'] = notfound_product
        else:
            data['notfound_failed'] = notfound_product

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def delete_product_from_notfound_table(notfound_table, id):
    key = {'productId': {'S': id}}
    condition = {':productId': {'S': id}}

    try:
        logger.info("Deleting product item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=notfound_table,
            Key=key,
            ConditionExpression="productId = :productId",
            ExpressionAttributeValues=condition
        )
        logger.info("Delete response: {}".format(response))
    except Exception as e:
        logger.error("Product could not be deleted. Exception: {}".format(e))
        return False

    return True


def add_product_items(lists_table, items):
    adds = {"added": [], "failed": []}

    for item in items:
        try:
            logger.info("Put product item: {}".format(item))
            response = dynamodb.put_item(
                TableName=lists_table,
                Item=item,
                ConditionExpression='attribute_not_exists(PK)'
            )
            logger.info("Add response: {}".format(response))
            adds['added'].append(item)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                logger.error("Product {} already exists in list {}.".format(item['SK']['S'], item['PK']['S']))
            else:
                logger.error("Product could not be created: {}".format(e))

            adds['failed'].append(item)

    return adds


def delete_notfound_items(lists_table, items):
    deletes = {"deleted": [], "failed": []}

    for item in items:
        key = {'PK': {'S': item['PK']['S']}, 'SK': {'S': item['SK']['S']}}

        condition = {':PK': {'S': item['PK']['S']}, ':SK': {'S': item['SK']['S']}}

        try:
            logger.info("Deleting product item: {}".format(key))
            response = dynamodb.delete_item(
                TableName=lists_table,
                Key=key,
                ConditionExpression="PK = :PK AND SK = :SK",
                ExpressionAttributeValues=condition
            )
            logger.info("Delete response: {}".format(response))
            deletes['deleted'].append(item)
        except Exception as e:
            logger.error("Product could not be deleted. Exception: {}".format(e))
            deletes['failed'].append(item)

    return deletes


def build_list_product_items(items, products_id):
    product_items = copy.deepcopy(items)

    for item in product_items:
        if "PRODUCT#" in item['SK']['S']:
            item['SK']['S'] = "PRODUCT#" + products_id
            item['type']['S'] = "products"
        elif "RESERVED#" in item['SK']['S']:
            sk_split = item['SK']['S'].split("#")
            item['SK']['S'] = "RESERVED#" + products_id + "#" + sk_split[2]
            item['productId']['S'] = products_id

    return product_items


def find_product_and_reserved_items(items, notfound_id):
    related_items = []

    for item in items:
        logger.debug("Checking response item: {}".format(item))
        if item['SK']['S'] == "PRODUCT#" + notfound_id:
            logger.info("Adding product item ({})".format(item))
            related_items.append(item)
        elif "RESERVED#" + notfound_id in item['SK']['S']:
            logger.info("Adding reserved item ({})".format(item))
            related_items.append(item)

    return related_items


def get_all_list_items(lists_table, list_id):
    try:
        response = dynamodb.query(
            TableName=lists_table,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        logger.info("Response: " + json.dumps(response))
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
        logger.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting pending lists from table.")

    if len(response['Items']) == 0:
        raise Exception("No lists for product {} were returned.".format(notfound_id))

    if len(response['Items']) > 1:
        raise Exception("Too many list items for product {} returned [{}].".format(notfound_id, response['Items']))

    return response['Items'][0]['PK']['S'].split("#")[1]


def put_product_in_products_table(products_table, new_product):
    id = str(uuid.uuid4())
    new_product['productId'] = {'S': id}

    try:
        logger.info("Product item to be put in table: {}".format(new_product))
        dynamodb.put_item(TableName=products_table, Item=new_product)
    except Exception as e:
        logger.error("Product could not be created: {}".format(e))
        raise Exception('Product could not be created.')

    return id


def build_products_item(notfound_product, new_product_details):
    product = {
        "brand": {'S': new_product_details['brand']},
        "details": {'S': new_product_details['details']},
        "retailer": {'S': new_product_details['retailer']},
        "imageUrl": {'S': new_product_details['imageUrl']},
        "productUrl": {'S': notfound_product['productUrl']['S']}
    }

    return product


def get_product_from_notfound(notfound_table, id):
    key = {'productId': {'S': id}}

    try:
        response = dynamodb.get_item(
            TableName=notfound_table,
            Key=key
        )
    except ClientError as e:
        logger.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    logger.info("Get product item response: {}".format(response))

    if 'Item' not in response:
        raise Exception("No product returned for the id {}.".format(id))

    return response['Item']
