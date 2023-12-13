# from typing import Annotated
import sqlite3
from fastapi import Depends, HTTPException, Header, status, APIRouter
from .db_connection import get_db
from .enrollment_helper import enroll_students_from_waitlist, is_auto_enroll_enabled

instructor_router = APIRouter()

@instructor_router.get("/classes/{class_id}/students")
def get_current_enrollment(class_id: int,
              instructor_id: int = Header(
                  alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
              db: sqlite3.Connection = Depends(get_db)):
    """
    Retreive current enrollment for the classes.

    Parameters:
    - class_id (int): The ID of the class.

    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
        result = db.execute(
            """
            SELECT stu.* 
            FROM class sec
                INNER JOIN enrollment e ON sec.id = e.class_id
                INNER JOIN student stu ON e.student_id = stu.id 
            WHERE sec.id=? AND sec.instructor_id=?
            """, [class_id, instructor_id]
        )
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    finally:
        return {"students": result.fetchall()}

@instructor_router.get("/classes/{class_id}/waitlist/")
def get_waitlist(
    class_id:int,
    instructor_id: int = Header(
        alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
    db: sqlite3.Connection = Depends(get_db)):
    """
    Retreive current waiting list for the class.

    Parameters:
    - class_id (int): The ID of the class.

    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
        result = db.execute(
            """
            SELECT stu.id, stu.first_name, stu.last_name, w.waitlist_date
            FROM class c
                INNER JOIN waitlist w ON c.id = w.class_id
                INNER JOIN student stu ON w.student_id = stu.id 
            WHERE c.id=? AND c.instructor_id=?
            ORDER BY w.waitlist_date ASC
            """, [class_id, instructor_id]
        )
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    finally:
        return {"students": result.fetchall()}

@instructor_router.get("/classes/{class_id}/droplist/")
def get_droplist(class_id: int,
              instructor_id: int = Header(
                  alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
              db: sqlite3.Connection = Depends(get_db)):
    """
    Retreive students who have dropped the class.

    Parameters:
    - class_id (int): The ID of the class.
    - instructor_id (int, In the header): A unique ID for students, instructors, and registrars.
    
    Returns:
    - dict: A dictionary containing the details of the classes
    """
    try:
        result = db.execute(
            """
            SELECT stu.* 
            FROM class c
                INNER JOIN droplist d ON c.id = d.class_id
                INNER JOIN student stu ON d.student_id = stu.id 
            WHERE c.id=? AND c.instructor_id=?
            """, [class_id, instructor_id]
        )
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    finally:
        return {"students": result.fetchall()}

@instructor_router.delete("/enrollment/{class_id}/{student_id}/administratively/", status_code=status.HTTP_200_OK)
def drop_class(
    class_id: int,
    student_id: int,
    instructor_id: int = Header(
        alias="x-cwid", description="A unique ID for students, instructors, and registrars"),
    db: sqlite3.Connection = Depends(get_db)
):
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
        curr = db.execute(
            """
            DELETE 
            FROM enrollment
            WHERE class_id = ? AND student_id=? 
                AND class_id IN (SELECT id 
                                    FROM "class" 
                                    WHERE id=? AND instructor_id=?);
            """, [class_id, student_id, class_id, instructor_id])

        if curr.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Record Not Found"
            )
        
        db.execute(
            """
            INSERT INTO droplist (class_id, student_id, drop_date, administrative) 
            VALUES (?, ?, datetime('now'), 1);
            """, [class_id, student_id]
        )
        db.commit()

        # Trigger auto enrollment
        if is_auto_enroll_enabled(db):        
            enroll_students_from_waitlist(db, [class_id])

    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return {"detail": "Item deleted successfully"}