from typing import Annotated
import boto3
import botocore
from fastapi import Depends, HTTPException, Header, Body, status, APIRouter, Response

from fastapi.responses import JSONResponse

import hashlib
from notification_service.email_notification import emit_log
from .db_connection import get_db
from .ddb_enrollment_schema import *
from boto3.dynamodb.conditions import Key
from datetime import datetime
import redis
from .ddb_enrollment_helper import DynamoDBRedisHelper

dynamodb_resource = boto3.resource('dynamodb', region_name='local')
redis_conn = redis.Redis(decode_responses=True)
ddb_helper_instance = DynamoDBRedisHelper(dynamodb_resource, redis_conn)

class_table_manager = Class(dynamodb_resource)

WAITLIST_CAPACITY = 15
MAX_NUMBER_OF_WAITLISTS_PER_STUDENT = 3

student_router = APIRouter()

@student_router.get("/classes/available/")
def get_available_classes(db: boto3.resource = Depends(get_db)):
    try: 
        available_classes = []

        class_table_instance = create_table_instance(Class, "class_table")
        enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")

        response = class_table_instance.scan()

        items = response.get('Items', [])

        for item in items:
            class_id = item['id']
            room_capacity = item['room_capacity']
            enrollments = enrollment_table_instance.query(KeyConditionExpression=Key('class_id').eq(class_id))
            num_of_enrollments = len(enrollments.get('Items', []))
            if num_of_enrollments < room_capacity:
                available_classes.append(item)

        for item in available_classes:
            print(item)

        return {"available_classes" : available_classes}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving classes: {str(e)}")
    
@student_router.post("/enrollment/")
def enroll(class_id: Annotated[int, Body(embed=True)],
           student_id: int = Header(
               alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
           first_name: str = Header(alias="x-first-name"),
           last_name: str = Header(alias="x-last-name")):
    """
    Student enrolls in a class

    Parameters:
    - class_id (int, in the request body): The unique identifier of the class where students will be enrolled.
    - student_id (int, in the request header): The unique identifier of the student who is enrolling.

    Returns:
    - HTTP_200_OK on success

    Raises:
    - HTTPException (400): If there are no available seats.
    - HTTPException (404): If the specified class does not exist.
    - HTTPException (409): If a conflict occurs (e.g., The student has already enrolled into the class).
    - HTTPException (500): If there is an internal server error.
    """

    try:
        print(f"Enrolling student {student_id} in class {class_id}")
        class_table_instance = create_table_instance(Class, "class_table")
        print("Class table instance created")
        
        enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")
        print("Enrollment table instance created")

        class_id = str(class_id)
        #class_id = int(class_id)
        
        student_id = str(student_id)
        print(f"Querying class table for class_id: {class_id}")
        
        response = class_table_instance.query(KeyConditionExpression=Key('id').eq(class_id))
        if not response.get('Items'):
            raise HTTPException(status_code=404, detail="Class not found")
        
        class_item = response.get('Items', [])[0]
        
        room_capacity = class_item['room_capacity']
        print(f"Room capacity for class {class_id}: {room_capacity}")
        
        print(f"Querying enrollment table for class_id: {class_id}")
        enrollments = enrollment_table_instance.query(KeyConditionExpression=Key('class_id').eq(class_id))
        
        num_of_enrollments = len(enrollments.get('Items', []))
        print(f"Number of enrollments in class {class_id}: {num_of_enrollments}")
        
        if num_of_enrollments < room_capacity:
            enrollment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item_to_add = {
                "class_id": class_id,
                "enrollment_date": enrollment_date,
                "student_id" : student_id
            }

            # Debugging statements
            print(f"Class ID: {class_id}, Type: {type(class_id)}")
            print(f"Enrollment Date: {enrollment_date}, Type: {type(enrollment_date)}")
            print(f"Student ID: {student_id}, Type: {type(student_id)}")
            
            enrollment_table_instance.put_item(Item=item_to_add)
            return {"message": "Enrollment successful"}

        else:
            print(f"Class {class_id} is full. Checking waitlist for student {student_id}")
            
            # Check the number of waitlists the student is already on
            waitlist_pattern = f"waitlist_*_{student_id}"
            waitlists = redis_conn.keys(waitlist_pattern)
            print(f"Student {student_id} is currently on {len(waitlists)} waitlists")

            if len(waitlists) >= MAX_NUMBER_OF_WAITLISTS_PER_STUDENT:
                print(f"Student {student_id} has reached the maximum waitlist limit")

                raise HTTPException(status_code=400, detail="Maximum waitlist limit reached.")
            
            
            # Add to waitlist
            #waitlist_key = f"waitlist_{class_id}_{student_id}"
            waitlist_key = f"waitlist_{class_id}"
            #waitlist_score = datetime.now().timestamp()  # Using current timestamp as score for FIFO
            waitlist_score = datetime.now().timestamp()
            #redis_conn.zadd(waitlist_key, {student_id: waitlist_score})
            redis_conn.zadd(waitlist_key, {student_id: waitlist_score})
            
            # Update TimeStamp for caching
            redis_conn.set(f"last-modified_{class_id}", datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
            
            print(f"Added student {student_id} to waitlist for class {class_id}")
            return {"message": "Added to waitlist"}
            #raise HTTPException(status_code=200, detail="Added to waitlist")
            
           
    except botocore.exceptions.ClientError as e:
        print(f"Botocore Client Error: {e}")
        raise HTTPException(status_code=500, detail=f"Botocore Client Error: {e}")

    except Exception as e:
        print(f"Error during enrollment process: {e}")
        raise HTTPException(status_code=500, detail=f"Error during enrollment process: {str(e)}")
    


@student_router.delete("/enrollment/{class_id}", status_code=status.HTTP_200_OK)
def drop_class(
    class_id: int,
    student_id: int = Header(
        alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
    db: boto3.resource = Depends(get_db)
):
    """
    Handles a DELETE request to drop a student (himself/herself) from a specific class.

    Parameters:
    - class_id (int): The ID of the class from which the student wants to drop.
    - student_id (int, in the header): A unique ID for students, instructors, and registrars.

    Returns:
    - dict: A dictionary with the detail message indicating the success of the operation.

    Raises:
    - HTTPException (404): If the specified enrollment record is not found.
    - HTTPException (409): If a conflict occurs.
    """
    try:

        enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")
        class_id = str(class_id)
        student_id = str(student_id)


        print("Iam here 1")

        # New code to check if table exists
        #existing_tables = [table.name for table in dynamodb_resource.tables.all()]
        #if "enrollment_table" not in existing_tables:
        #    print("Error: 'enrollment_table' does not exist.")

        #else:
            # Check if the enrollment record exists
        enrollment_response = enrollment_table_instance.query(
            KeyConditionExpression=Key('class_id').eq(class_id) & Key('student_id').eq(str(student_id))
        )
        enrollment_items = enrollment_response.get('Items', [])

        #print("Iam here 2")

        if not enrollment_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
            )

        # Delete the enrollment record
        enrollment_table_instance.delete_item(
            Key={
                'class_id': class_id,
                'student_id': str(student_id)
            }
        )

        # Insert into Droplist
        droplist_table_instance = create_table_instance(Droplist, "droplist_table")
        droplist_table_instance.put_item(
            Item={
                "class_id": class_id,
                "student_id": str(student_id),
                "drop_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "administrative": False
            }
        )

        # Trigger auto enrollment using the instance
        if ddb_helper_instance.is_auto_enroll_enabled():        
            ddb_helper_instance.enroll_students_from_waitlist([class_id])
            # Update TimeStamp for caching
            redis_conn.set(f"last-modified_{class_id}", datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))

    except botocore.exceptions.ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return {"detail": "Item deleted successfully"}




@student_router.get("/waitlist/{class_id}/position/")
def get_current_waitlist_position(
    class_id: int,
    student_id: int = Header(
        alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
    if_modified_since: str = Header(None)):
    """
    Retrieve waitlist position

    Returns:
    - dict: A dictionary containing the user's waitlist position info

    Raises:
    - HTTPException: If error occurs in retrieving position
    """
    try:
        redis_conn = redis.Redis(decode_responses=True)
        last_modified = redis_conn.get(f"last-modified_{class_id}")
        # Use the last-modified value directly since it's a string
        last_modified = last_modified if last_modified else datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        # Compare with If-Modified-Since header
        print(last_modified, "First Time")
        if last_modified <= if_modified_since:
            return Response(status_code=status.HTTP_304_NOT_MODIFIED)


        waitlist_key = f"waitlist_{class_id}"
        waitlist_position = redis_conn.zrank(waitlist_key, student_id)

        if waitlist_position is not None:
            waitlist_position += 1  # Adjust for zero-based index
            return JSONResponse(content={"class_id": class_id, "waitlist_position": waitlist_position}, headers={"Last-Modified": last_modified})

        else:
            message = f"You are not in the waitlist for class {class_id}"
            return JSONResponse(content={"class_id": class_id, "message": message})

    except redis.exceptions.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving waitlist position: {str(e)}")



@student_router.delete("/waitlist/{class_id}/")
def remove_from_waitlist(
    class_id: int,
    student_id: int = Header(
        alias="x-cwid", description="A unique ID for students, instructors, and registrars")):
    """
    Remove a student from the waitlist

    Returns:
    - dict: A message indicating successful removal

    Raises:
    - HTTPException: If student is not found on the waitlist
    """
    try:
        redis_conn = redis.Redis(decode_responses=True)
        waitlist_key = f"waitlist_{class_id}"

        if not redis_conn.zrem(waitlist_key, student_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found in Redis"
            )

        # Update TimeStamp for caching
        redis_conn.set(f"last-modified_{class_id}", datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        
        return {"detail": "Item deleted successfully"}

    except redis.exceptions.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Error removing from waitlist: {str(e)}")
    
