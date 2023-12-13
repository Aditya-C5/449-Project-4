import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Droplist:
    """Encapsulates an Amazon DynamoDB table for configurations."""

    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = None

    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table for configurations.

        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "class_id", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "student_id", "KeyType": "RANGE"} # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "class_id", "AttributeType": "S"},
                    {"AttributeName": "student_id", "AttributeType": "S"}
                    #{"AttributeName": "drop_date", "AttributeType": "S"},
                    #{"AttributeName": "administrative", "AttributeType": "BOOL"}
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table

# Create a Boto3 DynamoDB resource
dynamodb_resource = boto3.resource(
    'dynamodb',
    #aws_access_key_id='fakeMyKeyId',
    #aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:5300'
)

# Instantiate the Droplist class
droplist_table_manager = Droplist(dynamodb_resource)

table_name = "droplist_table"  # Provide a suitable table name
droplist_table_manager.create_table(table_name)

if droplist_table_manager.table:
    # The table exists, and you can perform operations on it
    print("Table name:", droplist_table_manager.table.table_name)