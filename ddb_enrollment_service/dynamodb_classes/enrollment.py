import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Enrollment:
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
                    #{"AttributeName": "enrollment_date", "AttributeType": "S"}
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

def create_enrollment_instance():
    dynamodb_resource = boto3.resource(
        'dynamodb',
        aws_access_key_id='fakeMyKeyId',
        aws_secret_access_key='fakeSecretAccessKey',
        endpoint_url='http://localhost:5300'
    )
    return Enrollment(dynamodb_resource)

# Create a Boto3 DynamoDB resource
dynamodb_resource = boto3.resource(
    'dynamodb',
    #aws_access_key_id='fakeMyKeyId',
    #aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:5300'
)

# Instantiate the Droplist class
enrollment_table_manager = Enrollment(dynamodb_resource)

table_name = "enrollment_table"  # Provide a suitable table name
enrollment_table_manager.create_table(table_name)

if enrollment_table_manager.table:
    # The table exists, and you can perform operations on it
    print("Table name:", enrollment_table_manager.table.table_name)