import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Class:
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
                    {"AttributeName": "id", "KeyType": "HASH"} # Partition key
                    #{"AttributeName": "dept_code", "KeyType": "RANGE"} # Sort Key (Questionable choice)
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"}
                    #{"AttributeName": "dept_code", "AttributeType": "S"},
                    #{"AttributeName": "course_num", "AttributeType": "N"},
                    #{"AttributeName": "section_no", "AttributeType": "N"},
                    #{"AttributeName": "academic_year", "AttributeType": "N"},
                    #{"AttributeName": "semester", "AttributeType": "S"},
                    #{"AttributeName": "instructor_id", "AttributeType": "S"},
                    #{"AttributeName": "room_num", "AttributeType": "S"},
                    #{"AttributeName": "room_capacity", "AttributeType": "N"},
                    #{"AttributeName": "course_start_date", "AttributeType": "S"},
                    #{"AttributeName": "enrollment_start", "AttributeType": "S"},
                    #{"AttributeName": "enrollment_end", "AttributeType": "S"},
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

def create_class_instance():
    dynamodb_resource = boto3.resource(
        'dynamodb',
        aws_access_key_id='fakeMyKeyId',
        aws_secret_access_key='fakeSecretAccessKey',
        endpoint_url='http://localhost:5300'
    )
    return Class(dynamodb_resource)

# Create a Boto3 DynamoDB resource
dynamodb_resource = boto3.resource(
    'dynamodb',
    #aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    #aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url='http://localhost:5300'
)

# Instantiate the Movies class
class_table_manager = Class(dynamodb_resource)


table_name = "class_table"  # Provide a suitable table name

class_table_manager.create_table(table_name)

if class_table_manager.table:
    # The table exists, and you can perform operations on it
    print("Table name:", class_table_manager.table.table_name)
