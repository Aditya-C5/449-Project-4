import boto3
from botocore.exceptions import ClientError
import logging
from decimal import Decimal

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


    def add_movie(self, title, year, plot, rating):
        """
        Adds a movie to the table.

        :param title: The title of the movie.
        :param year: The release year of the movie.
        :param plot: The plot summary of the movie.
        :param rating: The quality rating of the movie.
        """
        try:
            self.table.put_item(
                Item={
                    "year": year,
                    "title": title,
                    "info": {"plot": plot, "rating": Decimal(str(rating))},
                }
            )
        except ClientError as err:
            logger.error(
                "Couldn't add movie %s to table %s. Here's why: %s: %s",
                title,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

# Create a Boto3 DynamoDB resource
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

# Add a movie
movies_table_manager.add_movie("Snatch", 2000, "Plot Summary", 8.5)


