import json
import sys
import boto3

table_name = sys.argv[1]
file_name = sys.argv[2]


# usage: python bulk_load_table.py products-test ../../ewelists.com-web/src/views/ArticlePages/Products/BabyEssentials.json
# usage: python bulk_load_table.py products-staging ../../ewelists.com-web/src/views/ArticlePages/Products/BabyEssentials.json
# usage: python bulk_load_table.py products-prod ../../ewelists.com-web/src/views/ArticlePages/Products/BabyEssentials.json


dynamodb = boto3.resource('dynamodb')

try:
    table = dynamodb.Table(table_name)
except Exception as e:
    print("Could not connect to table. Error:" + e)

items = []

try:
    with open(file_name) as f:
        d = json.load(f)
        for p in d:
            items.append(d[p])

    with table.batch_writer() as batch:
        for item in items:
            print("Adding item [{}] to table [{}]".format(item['productId'], table_name))
            batch.put_item(Item=item)

except Exception as e:
    print("Unexpected Error:" + e)


# Old
# Test setup
# usage: python bulk_load_table.py lists-test ../Lists/data/lists-test.json
# usage: python bulk_load_table.py products-test products-test.json
# usage: python bulk_load_table.py notfound-test notfound-test.json

# Staging setup
# usage: python bulk_load_table.py lists-staging ../Lists/data/lists-staging.json
# usage: python bulk_load_table.py products-staging products-test.json
# usage: python bulk_load_table.py notfound-staging notfound-test.json
# try:
#     with open(file_name, 'r') as f:
#         for row in f:
#             items.append(json.loads(row))
#
#     with table.batch_writer() as batch:
#         for item in items:
#             print("Adding item [{}] to table [{}]".format(item['productId'], table_name))
#             # batch.put_item(Item=item)
#
# except Exception as e:
#     print("Unexpected Error:" + e)
