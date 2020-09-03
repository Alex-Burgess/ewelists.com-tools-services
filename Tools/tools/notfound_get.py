import json
import os
import boto3
from tools import common, logger
from tools.common_entities import Notfound
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    try:
        notfound_table_name = common.get_env_variable(os.environ, 'NOTFOUND_TABLE_NAME')
        lists_table_name = common.get_env_variable(os.environ, 'LISTS_TABLE_NAME')
        id = common.get_path_id(event)

        data = get_item(notfound_table_name, id)

        data['creatorsName'] = get_user(lists_table_name, data['createdBy'])
        data['listId'] = get_list_id(lists_table_name, id)
        if data['listId']:
            data['listTitle'] = get_list_title(lists_table_name, data['listId'], data['createdBy'])
        else:
            data['listTitle'] = 'Unknown'

        response = common.create_response(200, json.dumps(data))
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    return response


def get_user(table_name, id):
    key = {
        'PK': {'S': 'USER#' + id},
        'SK': {'S': 'USER#' + id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting user from lists table.")

    log.info("Get user response: {}".format(response))

    if 'Item' not in response:
        return None

    return response['Item']['name']['S']


def get_list_title(table_name, list_id, user_id):
    key = {
        'PK': {'S': 'LIST#' + list_id},
        'SK': {'S': 'USER#' + user_id}
    }

    log.info("Querying for key in lists table: {}".format(key))

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting list from lists table.")

    log.info("Get list response: {}".format(response))

    if 'Item' not in response:
        return None

    return response['Item']['title']['S']


def get_list_id(table_name, id):
    log.info("Querying for SK in lists table: PRODUCT#{}".format(id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName='SK-index',
            KeyConditionExpression="SK = :SK",
            ExpressionAttributeValues={":SK":  {'S': "PRODUCT#{}".format(id)}}
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem querying for list in lists table.")

    log.info("List Query response: {}".format(response))

    if len(response['Items']) == 0:
        return None

    return response['Items'][0]['PK']['S'].split("#")[1]


def get_item(table_name, id):
    log.info("Querying table for product id: {}".format(id))

    key = {'productId': {'S': id}}

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    log.info("Get item response: {}".format(response))

    if 'Item' not in response:
        raise Exception("No product exists with id: {}".format(id))

    product = Notfound(response['Item']).get_product()

    return product
