from typing import Annotated
import boto3
from redis import Redis
from datetime import datetime
from fastapi import Depends, HTTPException, Header, Body, status, APIRouter
from .db_connection import get_db, get_redis_db
from .ddb_enrollment_schema import *
from boto3.dynamodb.conditions import Key
WAITLIST_CAPACITY = 15
MAX_NUMBER_OF_WAITLISTS_PER_STUDENT = 3

instructor_router = APIRouter()

@instructor_router.get("/classes/{class_id}/students")
def get_current_enrollment(class_id: str,
              db: boto3.resource = Depends(get_db)):
    """
    Retreive current enrollment for the classes.

    Parameters:
    - class_id (int): The ID of the class.

    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
       
        enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")
             
        response = enrollment_table_instance.query(KeyConditionExpression=Key('class_id').eq(str(class_id)))
        items = {'Items': response['Items']}
        #return response['Items']
        if items:
            return items
        else:
            return "none"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving drop list: {str(e)}")
    
@instructor_router.get("/classes/{class_id}/waitlist/")
def get_waitlist(class_id: str, db: Redis = Depends(get_redis_db)):
    """
    Retreive current waiting list for the class.

    Parameters:
    - class_id (int): The ID of the class.

    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
        return {"waitlist" : db.zrange(class_id,0,-1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving waitlist: {str(e)}")
    
@instructor_router.get("/classes/{class_id}/droplist/")
def get_droplist(class_id: str, db: boto3.resource = Depends(get_db)):
    """
    Retreive students who have dropped the class.

    Parameters:
    - class_id (int): The ID of the class.
    - instructor_id (int, In the header): A unique ID for students, instructors, and registrars.
    
    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
       
        droplist_table_instance = create_table_instance(Droplist, "droplist_table")
             
        response = droplist_table_instance.query(KeyConditionExpression=Key('class_id').eq(str(class_id)))
        items = {'Items': response['Items']}
        #return response['Items']
        if items:
            return items
        else:
            return "none"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving drop list: {str(e)}")

@instructor_router.delete("/enrollment/{class_id}/{student_id}/administratively/", status_code=status.HTTP_200_OK) 
def drop_class(class_id: str, student_id: str, db: boto3.resource = Depends(get_db)):
    """
    Handles a DELETE request to administratively drop a student from a specific class.

    Parameters:
    - class_id (int): The ID of the class from which the student is being administratively dropped.
    - student_id (int): The ID of the student being administratively dropped.
    - instructor_id (int, In the header): A unique ID for students, instructors, and registrars.

    Returns:
    - dict: A dictionary with the detail message indicating the success of the administrative drop.

    Raises:
    - HTTPException (409): If there is a conflict in the delete operation.
    """
    
    try:        
        delete_key = {
            'class_id': class_id,
            'student_id':student_id
        }

        put_item = {
            'class_id': class_id,
            'student_id': student_id,
            'drop_date': "2023-06-01 09:00:00",
            'administrative': True  
   
        }
        transact_items=[
                        {
                            'Delete': {
                                'TableName': 'enrollment_table',
                                'Key': delete_key
                            }
                        },
                        {
                            'Put': {
                                'TableName': 'droplist_table',
                                'Item': put_item
                            }
                        }
                    ] 
              
        response = db.meta.client.transact_write_items(TransactItems = transact_items)
        
        print("TransactWriteItems succeeded:", response)
        return {"detail": "Student successfully dropped from class."}
    except Exception as e:  
        raise HTTPException(status_code=500, detail=f"Error dropping student: {str(e)}")    