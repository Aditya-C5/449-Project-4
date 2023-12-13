from typing import Annotated
import sqlite3
from fastapi import Depends, Response, HTTPException, Body, status, APIRouter
from .db_connection import get_db
from .enrollment_helper import enroll_students_from_waitlist, get_available_classes_within_first_2weeks
from .models import Course, ClassCreate, ClassPatch

registrar_router = APIRouter()

@registrar_router.put("/auto-enrollment/")
def set_auto_enrollment(enabled: Annotated[bool, Body(embed=True)], db: sqlite3.Connection = Depends(get_db)):
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
        db.execute("UPDATE configs set automatic_enrollment = ?;", [enabled])
        db.commit()

        if enabled:
            opening_classes = get_available_classes_within_first_2weeks(db)
            enroll_students_from_waitlist(db, opening_classes)

    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return {"detail": f"Auto enrollment: {enabled}"}

@registrar_router.post("/courses/", status_code=status.HTTP_201_CREATED)
def create_course(
    course: Course, response: Response, db: sqlite3.Connection = Depends(get_db)
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
    record = dict(course)
    try:
        cur = db.execute(
            """
            INSERT INTO course(department_code, course_no, title)
            VALUES(:department_code, :course_no, :title)
            """, record)
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return record

@registrar_router.post("/classes/", status_code=status.HTTP_201_CREATED)
def create_class(
    body_data: ClassCreate, response: Response, db: sqlite3.Connection = Depends(get_db)
):
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
    record = dict(body_data)
    try:
        cur = db.execute(
            """
            INSERT INTO class(dept_code, course_num, section_no, 
                    academic_year, semester, instructor_id, room_num, room_capacity, 
                    course_start_date, enrollment_start, enrollment_end)
            VALUES(:dept_code, :course_num, :section_no,
                    :academic_year, :semester, :instructor_id, :room_num, :room_capacity, 
                    :course_start_date, :enrollment_start, :enrollment_end)
            """, record)
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    response.headers["Location"] = f"/classes/{cur.lastrowid}"
    return {"detail": "Success", "inserted_id": cur.lastrowid}

@registrar_router.delete("/classes/{id}", status_code=status.HTTP_200_OK)
def delete_class(
    id: int, response: Response, db: sqlite3.Connection = Depends(get_db)
):
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
    try:
        curr = db.execute("DELETE FROM class WHERE id=?;", [id])

        if curr.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
            )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return {"detail": "Item deleted successfully"}

@registrar_router.patch("/classes/{id}", status_code=status.HTTP_200_OK)
def update_class(
    id: int,
    body_data: ClassPatch,
    response: Response,
    db: sqlite3.Connection = Depends(get_db),
):
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
        # Excluding fields that have not been set
        data_fields = body_data.dict(exclude_unset=True)

        # Create a list of column-placeholder pairs, separated by commas
        keys = ", ".join(
            [f"{key} = ?" for index, key in enumerate(data_fields.keys())]
        )

        # Create a list of values to bind to the placeholders
        values = list(data_fields.values())  # List of values to be updated
        values.append(id)  # WHERE id = ?

        # Define a parameterized query with placeholders & values
        update_query = f"UPDATE class SET {keys} WHERE id = ?"

        # Execute the query
        curr = db.execute(update_query, values)

        # Raise exeption if Record not Found
        if curr.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
            )
        db.commit()
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return {"message": "Item updated successfully"}