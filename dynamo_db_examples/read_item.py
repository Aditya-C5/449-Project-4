import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class Movies:
    """Encapsulates an Amazon DynamoDB table of movie data."""

    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None

    def set_table(self, table_name):
        """Sets the DynamoDB table."""
        self.table = self.dyn_resource.Table(table_name)

    def get_movie(self, title, year):
        """
        Gets movie data from the table for a specific movie.

        :param title: The title of the movie.
        :param year: The release year of the movie.
        :return: The data about the requested movie.
        """
        try:
            response = self.table.get_item(Key={"year": year, "title": title})
        except ClientError as err:
            logger.error(
                "Couldn't get movie %s from table %s. Here's why: %s: %s",
                title,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Item"]

dynamodb_resource = boto3.resource(
    'dynamodb',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:5300'
)

# Instantiate the Movies class
movies_table_manager = Movies(dynamodb_resource)

# Set the DynamoDB table
table_name = "movie_table"
movies_table_manager.set_table(table_name)

# Get a movie
print(movies_table_manager.get_movie("Snatch", 2000))
