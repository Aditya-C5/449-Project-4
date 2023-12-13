import boto3
import redis
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from boto3.dynamodb.conditions import Key

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

        '''if "Item" in response:
            return response["Item"]["value"] == "1"
        else:
            return False'''

    
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
                    if student_email is not None:
                        print(f" [x] {student_email}")
                        emit_log(student_email, class_id)


        return total_enrolled_from_waitlist

    
    
    '''def enroll_students_from_waitlist(self, class_id_list):
        total_enrolled_from_waitlist = 0  # Tracks total enrollments from the waitlist across all classes

        for class_id in class_id_list:
            enrollment_table = self.dynamodb_resource.Table("enrollment_table")
            room_capacity = int(class_info.get("room_capacity", 0))
            # Fetch current enrollment count for this class
            current_enrollments = enrollment_table.query(
                KeyConditionExpression=Key('class_id').eq(class_id)
            )
            enrollment_count = len(current_enrollments.get('Items', []))

            available_spots = room_capacity - enrollment_count
            
            waitlist_key = f"waitlist_{class_id}"
            waitlist_members = self.redis_conn.zrange(waitlist_key, 0, available_spots - 1)
            #waitlist_members = self.redis_conn.zrange(waitlist_key, 0, -1)

            class_table = self.dynamodb_resource.Table("class_table")
            class_info = class_table.get_item(Key={"id": class_id}).get("Item", {})
            

            # Enroll students from waitlist if spots are available
            if available_spots > 0:
                #for waitlist_member in waitlist_members[:available_spots]:
                for waitlist_member in waitlist_members:
                    student_id = waitlist_member.split("_")[1]

                    enrollment_table.put_item(
                        Item={"class_id": class_id, "student_id": student_id, "enrollment_date": datetime.now().isoformat()}
                    )

                    self.redis_conn.zrem(waitlist_key, waitlist_member)
                    total_enrolled_from_waitlist += 1

        return total_enrolled_from_waitlist'''

    
    '''def enroll_students_from_waitlist(self, class_id_list):
        enrollment_count = 0

        for class_id in class_id_list:
            enrollment_table = self.dynamodb_resource.Table("enrollment_table")
            waitlist_key = f"waitlist_{class_id}"
            waitlist_members = self.redis_conn.zrange(waitlist_key, 0, -1)

            class_table = self.dynamodb_resource.Table("class_table")
            class_info = class_table.get_item(Key={"id": class_id}).get("Item", {})
            available_spots = class_info.get("room_capacity", 0) - class_info.get("enrollment_count", 0)

            for waitlist_member in waitlist_members[:available_spots]:
                student_id = waitlist_member.split("_")[1]

                enrollment_table.put_item(
                    Item={"class_id": class_id, "student_id": student_id, "enrollment_date": datetime.now().isoformat()}
                )

                self.redis_conn.zrem(waitlist_key, waitlist_member)

                enrollment_count += 1

        return enrollment_count'''

    '''def get_available_classes_within_first_2weeks(self):
        available_classes = []

        class_table = self.dynamodb_resource.Table("class_table")
        enrollment_table = self.dynamodb_resource.Table("enrollment_table")

        response = class_table.scan()

        items = response.get('Items', [])

        for item in items:
            class_id = item['id']
            room_capacity = item['room_capacity']
            enrollments = enrollment_table.query(KeyConditionExpression=Key('class_id').eq(class_id))
            num_of_enrollments = len(enrollments.get('Items', []))
            if num_of_enrollments < room_capacity:
                available_classes.append(item)

        return available_classes'''
    
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
