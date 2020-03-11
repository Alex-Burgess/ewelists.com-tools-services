import json
import boto3
import argparse

# Args
parser = argparse.ArgumentParser(description='Bulk add list items.')
parser.add_argument('file_prefix')
parser.add_argument('-e', '--env', choices=['staging', 'test'], help='An environment', required=True)
args = parser.parse_args()

lists_table_name = 'lists-' + args.env
products_table_name = 'products-' + args.env
notfound_table_name = 'notfound-' + args.env

lists_file = '/Users/alexburgess/Downloads/' + args.file_prefix + '_lists.json'
products_file = '/Users/alexburgess/Downloads/' + args.file_prefix + '_products.json'
notfound_file = '/Users/alexburgess/Downloads/' + args.file_prefix + '_notfound.json'


def load_file_items(file_name):
    try:
        with open(file_name, 'r') as f:
            items = json.load(f)

    except Exception as e:
        print('There was an issue loading the lists import file: " + file + ".\n')
        raise e

    return items


def add_to_table(items, table_name):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        with table.batch_writer() as batch:
            for item in items:
                if table_name == lists_table_name:
                    print("Adding item [{}] to table [{}]".format(item['PK'], table_name))
                else:
                    print("Adding item [{}] to table [{}]".format(item['productId'], table_name))

                batch.put_item(Item=item)

    except Exception as e:
        print("There was an issue loading items to the " + lists_table_name + " table")
        raise e


# Main
list_items = load_file_items(lists_file)
add_to_table(list_items, lists_table_name)

product_items = load_file_items(products_file)
add_to_table(product_items, products_table_name)

notfound_items = load_file_items(notfound_file)
add_to_table(notfound_items, notfound_table_name)
