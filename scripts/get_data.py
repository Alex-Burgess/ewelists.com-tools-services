import json
import boto3
import decimal
import argparse
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

# Args
parser = argparse.ArgumentParser(description='Get list items.')
parser.add_argument('name')
parser.add_argument('-e', '--env', choices=['prod', 'staging', 'test'], help='An environment', required=True)
parser.add_argument('-l', '--listid', help='A list id', required=True)
args = parser.parse_args()

list_id = args.listid
name = args.name

lists_table_name = 'lists-' + args.env
products_table_name = 'products-' + args.env
notfound_table_name = 'notfound-' + args.env

lists_file = '/Users/alexburgess/Downloads/' + name + '_lists.json'
products_file = '/Users/alexburgess/Downloads/' + name + '_products.json'
notfound_file = '/Users/alexburgess/Downloads/' + name + '_notfound.json'


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def query_lists_table(list_id):
    try:
        lists_table = dynamodb.Table(lists_table_name)

        response = lists_table.query(
            KeyConditionExpression=Key('PK').eq("LIST#{}".format(list_id))
        )
    except Exception as e:
        raise Exception("Unexpected error when getting lists from table." + str(e))

    return response['Items']


def get_product_items(product_ids, table_name):
    products = []
    for id in product_ids:
        key = {'productId': id}

        try:
            table = dynamodb.Table(table_name)

            response = table.get_item(
                Key=key
            )
        except Exception as e:
            raise Exception("Unexpected error when getting product from table." + str(e))

        if 'Item' not in response:
            raise Exception("No product exists with this ID: " + id)

        products.append(response['Item'])

    return products


def print_items(items, file):
    print("Writing to file: " + file + ".\n")
    with open(file, 'w') as f:
        json.dump(items, f, cls=DecimalEncoder)


def get_prod_ids(items):
    product_ids = []
    notfound_ids = []
    for item in items:
        if item['SK'].startswith("PRODUCT"):
            if item['type'] == 'products':
                id = item.get('SK').split("#")[1]
                product_ids.append(id)
            else:
                id = item.get('SK').split("#")[1]
                notfound_ids.append(id)

    return product_ids, notfound_ids


# Main
list_items = query_lists_table(list_id)
print_items(list_items, lists_file)

product_ids, notfound_ids = get_prod_ids(list_items)

product_items = get_product_items(product_ids, products_table_name)
print_items(product_items, products_file)

notfound_items = get_product_items(notfound_ids, notfound_table_name)
print_items(notfound_items, notfound_file)
