import os
import json
import mock
from tools import backup, logger

log = logger.setup_test_logger()

LISTS_TABLE = 'lists-unittest'
PRODUCTS_TABLE = 'products-unittest'

mock_backup_response = {
    'BackupDetails': {
        'BackupArn': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest/backup/01589359875426-94a9bf97',
        'BackupName': 'lists-unittest-daily-backup',
        'BackupSizeBytes': 1443,
        'BackupStatus': 'CREATING',
        'BackupType': 'USER',
        # 'BackupCreationDateTime': datetime.datetime(2020, 5, 13, 8, 51, 15, 426000, tzinfo=tzlocal())
    }
}

mock_list_response = {
    'BackupSummaries': [
        {
            'TableName': 'lists-unittest',
            'TableId': '47a26b8d-d9bf-4604-9cee-c5226c7c9808',
            'TableArn': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest',
            'BackupArn': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest/backup/01589363779198-02bfaf8f',
            'BackupName': 'lists-test-daily-backup',
            # 'BackupCreationDateTime': datetime.datetime(2020, 5, 13, 9, 56, 19, 198000, tzinfo=tzlocal()),
            'BackupStatus': 'AVAILABLE',
            'BackupType': 'USER',
            'BackupSizeBytes': 1443
        },
        {
            'TableName': 'lists-unittest',
            'TableId': '47a26b8d-d9bf-4604-9cee-c5226c7c9808',
            'TableArn': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest',
            'BackupArn': 'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest/backup/01589363891498-75452cc9',
            'BackupName': 'lists-test-daily-backup',
            # 'BackupCreationDateTime': datetime.datetime(2020, 5, 13, 9, 58, 11, 498000, tzinfo=tzlocal()),
            'BackupStatus': 'AVAILABLE',
            'BackupType': 'USER',
            'BackupSizeBytes': 1443
        }
    ]
}

mock_delete_response = {
    'BackupDescription': {
        'BackupDetails': {
            'BackupArn': 'string'
        }
    }
}


class TestHandler:
    @mock.patch("tools.backup.create_backup_call", mock.MagicMock(return_value=mock_backup_response))
    @mock.patch("tools.backup.list_backups_call", mock.MagicMock(return_value=mock_list_response))
    @mock.patch("tools.backup.delete_backup_call", mock.MagicMock(return_value=mock_delete_response))
    def test_success(self, monkeypatch, scheduled_event):
        monkeypatch.setitem(os.environ, 'LISTS_TABLE_NAME', LISTS_TABLE)
        monkeypatch.setitem(os.environ, 'PRODUCTS_TABLE_NAME', PRODUCTS_TABLE)
        monkeypatch.setitem(os.environ, 'RETENTION_DAYS', "7")

        response = backup.handler(scheduled_event, None)
        body = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        assert body['lists-unittest'], "Backup was not created"
        assert body['products-unittest'], "Backup was not created"


@mock.patch("tools.backup.create_backup_call", mock.MagicMock(return_value=mock_backup_response))
def test_create_backup():
    assert backup.create_backup(LISTS_TABLE), "Backup was not created."


@mock.patch("tools.backup.list_backups_call", mock.MagicMock(return_value=mock_list_response))
@mock.patch("tools.backup.delete_backup_call", mock.MagicMock(return_value=mock_delete_response))
def test_delete_old_backups():
    assert backup.delete_old_backups(LISTS_TABLE, "7"), "List Backups did not work."


def test_backup_name():
    name = backup.create_name(LISTS_TABLE)
    assert name == "lists-unittest-daily-backup", "backup name was wrong"


def test_get_date():
    date = backup.get_date("7")
    assert type(date).__name__ == "datetime", "Value was not a datetime class."


class TestGetBackupsToDelete:
    def test_get_backups_to_delete(self):
        arns = backup.get_backups_to_delete(mock_list_response)
        expected_arns = [
            'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest/backup/01589363779198-02bfaf8f',
            'arn:aws:dynamodb:eu-west-1:123456789012:table/lists-unittest/backup/01589363891498-75452cc9'
        ]

        assert arns == expected_arns, "List of arns was not as expected."

    def test_empty_response(self):
        empty_list_response = {
            'BackupSummaries': []
        }
        arns = backup.get_backups_to_delete(empty_list_response)

        assert arns == [], "List of arns was not as expected."
