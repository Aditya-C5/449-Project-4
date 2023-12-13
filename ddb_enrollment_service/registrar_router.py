from typing import Annotated
import boto3
from fastapi import Depends, Response, HTTPException, Body, status, APIRouter
from .db_connection import get_db
from .ddb_enrollment_schema import *
from boto3.dynamodb.conditions import Key
from .models import Course, ClassCreate, ClassPatch
WAITLIST_CAPACITY = 15
MAX_NUMBER_OF_WAITLISTS_PER_STUDENT = 3

registrar_router = APIRouter()

@registrar_router.put("/auto-enrollment/")
def set_auto_enrollment(enabled: Annotated[bool, Body(embed=True)], db: boto3.resource = Depends(get_db)):
    """
    Endpoint for enabling/disabling automatic enrollment.

    Parameters:
    - enabled (bool): A boolean indicating whether automatic enrollment should be enabled or disabled.

    Raises:
    - HTTPException (409): If there is an integrity error while updating the database.

    Returns:
        dict: A dictionary containing a detail message confirming the status of auto enrollment.
    """
    try:
        table = db.Table('configs_table')
        table.put_item(
            Item={
                'variable_name': 'automatic_enrollment',
                'value': enabled,
        }
)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving drop list: {str(e)}")

    return {"detail": f"Auto enrollment: {enabled}"}

@registrar_router.post("/classes/", status_code=status.HTTP_201_CREATED)
def create_class(body_data: ClassCreate, db: boto3.resource = Depends(get_db)):
    """
    Creates a new class.

    Parameters:
    - `class` (Class): The JSON object representing the class with the following properties:
        - `dept_code` (str): Department code.
        - `course_num` (int): Course number.
        - `section_no` (int): Section number.
        - `academic_year` (int): Academic year.
        - `semester` (str): Semester name (SP, SU, FA, WI).
        - `instructor_id` (int): Instructor ID.
        - `room_num` (int): Room number.
        - `room_capacity` (int): Room capacity.
        - `course_start_date` (str): Course start date (format: "YYYY-MM-DD").
        - `enrollment_start` (str): Enrollment start date (format: "YYYY-MM-DD HH:MM:SS.SSS").
        - `enrollment_end` (str): Enrollment end date (format: "YYYY-MM-DD HH:MM:SS.SSS").

    Returns:
    - dict: A dictionary containing the details of the created item.

    Raises:
    - HTTPException (409): If a conflict occurs (e.g., duplicate course).
    """
    try:
        class_table_instance = create_table_instance(Class, "class_table")

        item_to_add = {
            "id": body_data.id,
            "dept_code": body_data.dept_code,
            "course_num": body_data.course_num,
            "section_no": body_data.section_no,
            "academic_year": body_data.academic_year,
            "semester": body_data.semester,
            "instructor_id": body_data.instructor_id,
            "room_num": body_data.room_num,
            "room_capacity": body_data.room_capacity,
            "course_start_date": body_data.course_start_date,
            "enrollment_start": body_data.enrollment_start,
            "enrollment_end": body_data.enrollment_end,
        }

        class_table_instance.put_item(Item=item_to_add)

        return {"added to class table": item_to_add}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating class: {str(e)}")
    
@registrar_router.post("/courses/", status_code=status.HTTP_201_CREATED)
def create_course(course: Course, db: boto3.resource = Depends(get_db)
):
    """
    Creates a new course with the provided details.

    Parameters:
    - `course` (CourseInput): JSON body input for the course with the following fields:
        - `department_code` (str): The department code for the course.
        - `course_no` (int): The course number.
        - `title` (str): The title of the course.

    Returns:
    - dict: A dictionary containing the details of the created item.

    Raises:
    - HTTPException (409): If a conflict occurs (e.g., duplicate course).
    """
    try:
        table = db.Table('course_table')
        table.put_item(
            Item={
                'department_code': course.department_code,
                'course_no': course.course_no,
                'course_name': course.title
            }
        )   

        return {"Course created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course: {str(e)}")
        
@registrar_router.delete("/classes/{id}", status_code=status.HTTP_200_OK)
def delete_class(id: int, db: boto3.resource = Depends(get_db)):
    """
    Deletes a specific class.

    Parameters:
    - `id` (int): The ID of the class to delete.

    Returns:
    - dict: A dictionary indicating the success of the deletion operation.
      Example: {"message": "Item deleted successfully"}

    Raises:
    - HTTPException (404): If the class with the specified ID is not found.
    - HTTPException (409): If there is a conflict in the delete operation.
    """
    # TO DO create a variable name is_deleted, set it to true when calling this api instead of actually deleting the record
    
    try:
        table = db.Table('class_table')
        table.delete_item(
            Key={
                'id': str(id)
            }
        )  

        return {"message": "Item deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course: {str(e)}")

@registrar_router.patch("/classes/{id}", status_code=status.HTTP_200_OK)
def update_class(id: int, body_data: ClassPatch, db: boto3.resource = Depends(get_db)):
    """
    Updates specific details of a class.

    Parameters:
    - `class` (ClassPatch): The JSON object representing the class with the following properties:
        - `section_no` (int, optional): Section number.
        - `instructor_id` (int, optional): Instructor ID.
        - `room_num` (int, optional): Room number.
        - `room_capacity` (int, optional): Room capacity.
        - `course_start_date` (str, optional): Course start date (format: "YYYY-MM-DD").
        - `enrollment_start` (str, optional): Enrollment start date (format: "YYYY-MM-DD HH:MM:SS.SSS").
        - `enrollment_end` (str, optional): Enrollment end date (format: "YYYY-MM-DD HH:MM:SS.SSS").

    Returns:
    - dict: A dictionary indicating the success of the update operation.
      Example: {"message": "Item updated successfully"}

    Raises:
    - HTTPException (404): If the class with the specified ID is not found.
    - HTTPException (409): If there is a conflict in the update operation (e.g., duplicate class details).
    """
    try:
        table = db.Table('class_table')
        table.update_item(
            Key={
                'id': str(id),
            },
            UpdateExpression='SET instuctor_id = :val1',
            ExpressionAttributeValues={
                ':val1': body_data.instructor_id
            }
        )       

        return {"message": "Item updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")