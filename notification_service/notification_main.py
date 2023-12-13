from typing import Annotated, Optional
import boto3
import redis
from fastapi import Depends, HTTPException, Header, Body, status, APIRouter
from ddb_enrollment_service.db_connection import get_db
from ddb_enrollment_service.ddb_enrollment_schema import Class
from ddb_enrollment_service.ddb_enrollment_helper import DynamoDBRedisHelper
from boto3.dynamodb.conditions import Key
from datetime import datetime
import re
import logging
from botocore.exceptions import ClientError
#import validators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DynamoDB and Redis clients
dynamodb_resource = boto3.resource('dynamodb', region_name='local')
redis_conn = redis.Redis(decode_responses=True)

# Create an instance of the helper class
ddb_helper_instance = DynamoDBRedisHelper(dynamodb_resource, redis_conn)

# Initialize your table manager
class_table_manager = Class(dynamodb_resource)

# Constants
WAITLIST_CAPACITY = 15
MAX_NUMBER_OF_WAITLISTS_PER_STUDENT = 3

# Router
notification_router = APIRouter()

# Dependency for Redis client
def get_redis_client():
    return redis_conn


def is_valid_class_id(class_id: int) -> bool:
    #dynamodb_resource = boto3.resource('dynamodb', region_name='local', endpoint_url='http://localhost:8000')
    try:
        class_table = dynamodb_resource.Table("class_table") 
        response = class_table.get_item(Key={"id": str(class_id)})  # Convert to string
        return "Item" in response
    except ClientError as err:
        logger.error(f"Error accessing DynamoDB: {err}")
        return False



def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Basic email pattern
    return re.match(pattern, email) is not None



def is_valid_student_id(student_id: int) -> bool:
    #dynamodb_resource = boto3.resource('dynamodb', region_name='local', endpoint_url='http://localhost:8000')
    try:
        student_table = dynamodb_resource.Table("student_table")  
        response = student_table.get_item(Key={"id": str(student_id)})
        return "Item" in response
    except ClientError as err:
        logger.error(f"Error accessing DynamoDB: {err}")
        return False



#def is_valid_url(url: str) -> bool:
#    return validators.url(url)


# Endpoint to subscribe to notifications
@notification_router.post("/students/subscribe/", status_code=status.HTTP_201_CREATED, tags=["Student"])
def subscribe_to_notifications(
    student_id: int, 
    class_id: int,
    email: Optional[str] = None,
    webhook_url: Optional[str] = None,
    redis_client: redis.Redis = Depends(get_redis_client)
):
    
    # Ensure at least one of email or webhook_url is provided
    if not email and not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of email or webhook URL must be provided"
        )
    
    # Input Validation
    if not is_valid_class_id(class_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid class ID")

    if not is_valid_student_id(student_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid student ID")

    if email and not is_valid_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    #if webhook_url and not is_valid_url(webhook_url):
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook URL format")

    # Redis Key Generation
    email_key = f'notification_{class_id}_{student_id}_email'
    webhook_key = f'notification_{class_id}_{student_id}_proxy'

    # Handle Duplicate Subscriptions
    existing_email = redis_client.get(email_key)
    existing_webhook = redis_client.get(webhook_key)

    if existing_email or existing_webhook:
        # how to handle duplicates. For now overwrites them.
        pass

    # Storing Subscription in Redis
    if email:
        redis_client.set(email_key, email)
    if webhook_url:
        redis_client.set(webhook_key, webhook_url)

    return {"message": "Subscribed successfully to class notifications"}


'''# Endpoint to list subscriptions
@notification_router.get("/students/subscriptions/", status_code=status.HTTP_200_OK, tags=["Student"])
def list_subscriptions(student_id: int, redis_client: redis.Redis = Depends(get_redis_client)):
    # Fetch subscriptions from Redis
    subscriptions = fetch_student_subscriptions(student_id, redis_client)
    # ...

    return {"subscriptions": subscriptions}'''

@notification_router.get("/students/subscriptions/", status_code=status.HTTP_200_OK, tags=["Student"])
def list_subscriptions(student_id: int, redis_client: redis.Redis = Depends(get_redis_client)):
    # Pattern for matching student's subscriptions
    pattern = f'notification_*_{student_id}_*'

    # Fetch all keys matching the pattern
    subscription_keys = redis_client.keys(pattern)

    subscriptions = []
    for key in subscription_keys:
        # Split the key to extract course_id and subscription type
        _, course_id, _, subscription_type = key.split('_')
        subscription_value = redis_client.get(key)
        subscriptions.append({
            "course_id": course_id,
            "type": "email" if subscription_type == "email" else "webhook",
            "value": subscription_value
        })

    if not subscriptions:
        return {"message": "No subscriptions found for the student."}

    return {"subscriptions": subscriptions}




@notification_router.delete("/students/unsubscribe/", status_code=status.HTTP_200_OK, tags=["Student"])
def unsubscribe_from_course(
    student_id: int, course_id: int, redis_client: redis.Redis = Depends(get_redis_client)
):
    # Redis Key Generation
    email_key = f'notification_{course_id}_{student_id}_email'
    webhook_key = f'notification_{course_id}_{student_id}_proxy'

    # Check if the subscription exists
    existing_email = redis_client.get(email_key)
    existing_webhook = redis_client.get(webhook_key)

    if not existing_email and not existing_webhook:
        # No subscription found for the student in the course
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for the specified course and student."
        )

    # Deleting subscriptions from Redis
    if existing_email:
        redis_client.delete(email_key)
    if existing_webhook:
        redis_client.delete(webhook_key)

    return {"message": "Unsubscribed successfully from course"}


@notification_router.delete("/students/unsubscribe/", status_code=status.HTTP_200_OK, tags=["Student"])
def notification(
    student_id: int, course_id: int, redis_client: redis.Redis = Depends(get_redis_client)
):
    # Redis Key Generation
    email_key = f'notification_{course_id}_{student_id}_email'
    webhook_key = f'notification_{course_id}_{student_id}_proxy'

    # Check if the subscription exists
    existing_email = redis_client.get(email_key)
    existing_webhook = redis_client.get(webhook_key)

    if not existing_email and not existing_webhook:
        # No subscription found for the student in the course
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for the specified course and student."
        )

    # Deleting subscriptions from Redis
    if existing_email:
        redis_client.delete(email_key)
    if existing_webhook:
        redis_client.delete(webhook_key)

    return {"message": "Unsubscribed successfully from course"}

