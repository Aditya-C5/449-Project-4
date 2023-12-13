import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Instructor:
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
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                    #{"AttributeName": "last_name", "KeyType": "RANGE"} # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    #{"AttributeName": "first_name", "AttributeType": "S"},
                    #{"AttributeName": "last_name", "AttributeType": "S"},
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

# Instantiate the Instructor class
instructor_table_manager = Instructor(dynamodb_resource)

table_name = "instructor_table"  # Provide a suitable table name
instructor_table_manager.create_table(table_name)

if instructor_table_manager.table:
    # The table exists, and you can perform operations on it
    print("Table name:", instructor_table_manager.table.table_name)