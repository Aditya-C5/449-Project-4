import boto3
import redis

def get_db():

    dynamodb_resource = boto3.resource(
    'dynamodb',
    #aws_access_key_id='fakeMyKeyId',
    #aws_secret_access_key='fakeSecretAccessKey',
    endpoint_url='http://localhost:8000'
)
    return dynamodb_resource

def get_redis_db():
    return redis.Redis()