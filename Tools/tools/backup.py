import json
import boto3
import os
from datetime import datetime, timedelta
from tools import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    data = {}
    lists_table = common.get_env_variable(os.environ, 'LISTS_TABLE_NAME')
    products_table = common.get_env_variable(os.environ, 'PRODUCTS_TABLE_NAME')
    retention_days = common.get_env_variable(os.environ, 'RETENTION_DAYS')

    for table in [lists_table, products_table]:
        create_backup(table)
        delete_old_backups(table, retention_days)
        data[table] = True

    response = common.create_response(200, json.dumps(data))

    return response


def create_backup_call(table_name, backup_name):
    try:
        response = dynamodb.create_backup(
            TableName=table_name,
            BackupName=backup_name
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem creating backup.")

    return response


def list_backups_call(table_name, date):
    try:
        response = dynamodb.list_backups(
            TableName=table_name,
            TimeRangeUpperBound=date
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    return response


def delete_backup_call(arn):
    try:
        response = dynamodb.delete_backup(
            BackupArn=arn
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem deleting backup.")

    return response


def create_name(table_name):
    return table_name + "-daily-backup"


def create_backup(table_name):
    backup_name = create_name(table_name)
    backup_response = create_backup_call(table_name, backup_name)
    log.info("Backup arn: " + backup_response['BackupDetails']['BackupArn'])

    return True


def delete_old_backups(table_name, days):
    date = get_date(days)
    response = list_backups_call(table_name, date)
    log.info("Number of Backups after retention period: " + str(len(response['BackupSummaries'])))

    arns = get_backups_to_delete(response)

    for arn in arns:
        log.info("Deleting: " + arn)
        delete_backup_call(arn)

    return True


def get_backups_to_delete(response):
    arns = []
    for backup in response['BackupSummaries']:
        arns.append(backup['BackupArn'])

    log.info("Backup arns being deleted: " + str(arns))

    return arns


def get_date(days):
    date = datetime.now() - timedelta(days=int(days))
    log.info("Retention days: " + str(days))
    log.info("Retention date: " + str(date))

    return date
