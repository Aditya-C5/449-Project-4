import boto3
import redis
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Header
from boto3.dynamodb.conditions import Key
from starlette.responses import Response
import hashlib

from notification_service.email_notification import emit_log

# Create Boto3 DynamoDB resource
dynamodb_resource = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:5300'
)

# Create Redis connection
redis_conn = redis.Redis(decode_responses=True)

class DynamoDBRedisHelper:
    def __init__(self, dynamodb_resource, redis_conn):
        self.dynamodb_resource = dynamodb_resource
        self.redis_conn = redis_conn

    def is_auto_enroll_enabled(self):
        configs_table = self.dynamodb_resource.Table("configs_table")
        response = configs_table.get_item(Key={"variable_name": "automatic_enrollment"})

        if "Item" in response:
            return response["Item"]["value"] is True  # Check for boolean True
        else:
            return False

    
    def enroll_students_from_waitlist(self, class_id_list):
        total_enrolled_from_waitlist = 0  # Tracks total enrollments from the waitlist across all classes

        for class_id in class_id_list:
            # Retrieve class information
            class_table = self.dynamodb_resource.Table("class_table")
            class_info = class_table.get_item(Key={"id": class_id}).get("Item", {})
            room_capacity = int(class_info.get("room_capacity", 0))

            # Fetch current enrollment count for this class
            enrollment_table = self.dynamodb_resource.Table("enrollment_table")
            current_enrollments = enrollment_table.query(
                KeyConditionExpression=Key('class_id').eq(class_id)
            )
            enrollment_count = len(current_enrollments.get('Items', []))

            # Calculate available spots
            available_spots = room_capacity - enrollment_count

            # Proceed only if there are available spots
            if available_spots > 0:
                waitlist_key = f"waitlist_{class_id}"
                waitlist_members = self.redis_conn.zrange(waitlist_key, 0, available_spots - 1)

                for waitlist_member in waitlist_members:
                    # Enroll student from waitlist
                    student_id = waitlist_member
                    enrollment_table.put_item(
                        Item={"class_id": class_id, "student_id": student_id, "enrollment_date": datetime.now().isoformat()}
                    )

                    # Remove student from waitlist
                    self.redis_conn.zrem(waitlist_key, student_id)
                    total_enrolled_from_waitlist += 1
                    email_key = f'notification_{class_id}_{student_id}_email'
                    student_email = self.redis_conn.get(email_key)
                    print(f" [x] {student_email}")
                    redis_conn.set(f"last-modified_{class_id}", datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
                    if student_email is not None:
                        print(f" [x] {student_email}")
                        emit_log(student_email, class_id)


        return total_enrolled_from_waitlist

    '''def check_last_modified(class_id: int, if_modified_since: str = None):
        """
    Checks if the content has been modified since the date provided in the If-Modified-Since header.
    Updates the last modified timestamp in Redis if not present.

    Args:
        class_id (int): The ID of the class.
        if_modified_since (str): The date string from the If-Modified-Since header.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating whether the content is modified
                          and the last modified date string.
    """
        last_modified_key = f"last-modified_{class_id}"
        last_modified = redis_conn.get(last_modified_key)

        # If not present in Redis, set to current time
        if not last_modified:
            last_modified = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            redis_conn.set(last_modified_key, last_modified)

        # Compare with the If-Modified-Since header
        if if_modified_since and last_modified <= if_modified_since:
            # Content not modified
            return False, last_modified

        # Content modified
        return True, last_modified'''
    
    
    def process_waitlist(self, class_id):
        class_table = self.dynamodb_resource.Table("class_table")
        class_info = class_table.get_item(Key={"id": class_id}).get("Item", {})
        available_spots = class_info.get("room_capacity", 0) - class_info.get("enrollment_count", 0)

        if available_spots > 0:
            waitlist_key = f"waitlist_{class_id}"
            waitlist_members = self.redis_conn.zrange(waitlist_key, 0, available_spots - 1)

            for student_id in waitlist_members:
                # Enroll student
                enrollment_table = self.dynamodb_resource.Table("enrollment_table")
                enrollment_table.put_item(
                    Item={
                        "class_id": class_id,
                        "student_id": student_id,
                        "enrollment_date": datetime.now().isoformat()
                    }
                )
                # Remove from waitlist
                self.redis_conn.zrem(waitlist_key, student_id)

# Instantiate DynamoDBRedisHelper
helper = DynamoDBRedisHelper(dynamodb_resource, redis_conn)
