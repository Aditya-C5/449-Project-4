import boto3
from botocore.exceptions import ClientError
import logging
logging.basicConfig(level=logging.INFO)
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
            # Check if the table already exists
            existing_tables = [table.name for table in self.dyn_resource.tables.all()]
            if table_name in existing_tables:
                print(f"Table {table_name} already exists. Deleting the existing table.")
                existing_table = self.dyn_resource.Table(table_name)
                existing_table.delete()
                existing_table.wait_until_not_exists()

            # Create the new table
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
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
        
class Configs:
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
                    {"AttributeName": "variable_name", "KeyType": "HASH"},  # Partition key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "variable_name", "AttributeType": "S"},
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

class Course:
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
                    {"AttributeName": "department_code", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "course_no", "KeyType": "RANGE"} # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "department_code", "AttributeType": "S"},
                    {"AttributeName": "course_no", "AttributeType": "N"}
                    #{"AttributeName": "course_name", "AttributeType": "S"}
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
        
class Department:
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
                    {"AttributeName": "code", "KeyType": "HASH"}  # Partition key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "code", "AttributeType": "S"},
                    #{"AttributeName": "department_name", "AttributeType": "S"}
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
            # Check if the table already exists
            existing_tables = [table.name for table in self.dyn_resource.tables.all()]
            if table_name in existing_tables:
                print(f"Table {table_name} already exists. Deleting the existing table.")
                existing_table = self.dyn_resource.Table(table_name)
                existing_table.delete()
                existing_table.wait_until_not_exists()
                
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "class_id", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "student_id", "KeyType": "RANGE"} # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "class_id", "AttributeType": "S"},
                    {"AttributeName": "student_id", "AttributeType": "S"}
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
            # Check if the table already exists
            existing_tables = [table.name for table in self.dyn_resource.tables.all()]
            if table_name in existing_tables:
                print(f"Table {table_name} already exists. Deleting the existing table.")
                existing_table = self.dyn_resource.Table(table_name)
                existing_table.delete()
                existing_table.wait_until_not_exists()
                
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "class_id", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "student_id", "KeyType": "RANGE"} # Sort Key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "class_id", "AttributeType": "S"},  # Partition key
                    {"AttributeName": "student_id", "AttributeType": "S"},
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

class Student:
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
                    #{"AttributeName": "last_name", "AttributeType": "S"}
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
        
def create_table_instance(class_type, table_name):
    logging.info(f"Creating table instance for: {table_name}")
    dynamodb_resource = boto3.resource(
        'dynamodb',
        region_name='local',
        aws_access_key_id='65r0k8',
        aws_secret_access_key='mgumzh',
        endpoint_url='http://localhost:8000'
    )
    try:
        table_manager = class_type(dynamodb_resource)
        table_manager.table = table_manager.dyn_resource.Table(table_name)

        # Log table status
        status = table_manager.table.table_status
        logging.info(f"Table '{table_name}' status: {status}")

    except Exception as e:
        logging.error(f"Error in creating table instance for '{table_name}': {e}")
        raise

    return table_manager.table
    

def create_table(class_type, table_name): 
    dynamodb_resource = boto3.resource(
        'dynamodb',
        region_name='local',
        aws_access_key_id='f1v1v6',
        aws_secret_access_key='4j3k6',
        endpoint_url='http://localhost:8000'
    )
    table_manager = class_type(dynamodb_resource)
    table_manager.create_table(table_name)
    print(f"Table {table_name} created successfully.")

if __name__ == "__main__":
    
    # Initialize a Boto3 DynamoDB resource
    dynamodb_resource = boto3.resource(
        'dynamodb',
        region_name='local',
        #aws_access_key_id='65r0k8',
        #aws_secret_access_key='mgumzh',
        endpoint_url='http://localhost:8000'
    )

    # Define a list of table names to delete
    table_names = ["class_table", "configs_table", "enrollment_table", "course_table", "department_table", "droplist_table", "instructor_table", "student_table"]

    # Loop through the table names and delete each table
    for table_name in table_names:
        table = dynamodb_resource.Table(table_name)
        try:
            table.delete()
            print(f"Table {table_name} deleted successfully.")
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")

    # Create the tables    
    create_table(Class, "class_table")
    create_table(Configs, "configs_table")
    create_table(Enrollment, "enrollment_table")
    create_table(Course, "course_table")
    create_table(Department, "department_table")
    create_table(Droplist, "droplist_table")
    create_table(Instructor, "instructor_table")
    create_table(Student, "student_table")