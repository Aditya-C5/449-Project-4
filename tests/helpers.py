import os
import requests
from tests.settings import *

def unittest_setUp():
    if USING_LITEFS_TO_REPLICATE_USER_DATABASE:
        # ------- If you're using LiteFS, READ ME -----------
        # In case of using LiteFS to replicate user service database,
        # the data in user database will be reset.

        # Delete the current database, then create a new one
        os.system(f"[ ! -f {USER_DB_PATH} ] || rm {USER_DB_PATH}")
        os.system("sh ./bin/create-user-db.sh > /dev/null")
    else:
        # Backup the current database, then create a new one
        os.system(f"[ ! -f {USER_DB_PATH} ] || cp {USER_DB_PATH} {USER_DB_PATH}.backup")
        os.system("sh ./bin/create-user-db.sh > /dev/null")

    # Backup Enrollment service database
    os.system(f"[ ! -f {ENROLLMENT_DB_PATH} ] || mv {ENROLLMENT_DB_PATH} {ENROLLMENT_DB_PATH}.backup")
    os.system("sh ./bin/create-enrollment-db.sh > /dev/null")

def unittest_tearDown():
    if USING_LITEFS_TO_REPLICATE_USER_DATABASE:
        os.system(f"[ ! -f {USER_DB_PATH} ] || rm {USER_DB_PATH}")
        os.system("sh ./bin/create-user-db.sh > /dev/null")
    else:
        # Restore database
        os.system(f"rm -f {USER_DB_PATH}")
        os.system(f"[ ! -f {USER_DB_PATH}.backup ] || mv {USER_DB_PATH}.backup {USER_DB_PATH}")

    # Restore Enrollment service database
    os.system(f"rm -f {ENROLLMENT_DB_PATH}")
    os.system(f"[ ! -f {ENROLLMENT_DB_PATH}.backup ] || mv {ENROLLMENT_DB_PATH}.backup {ENROLLMENT_DB_PATH}")

def user_register(user_id, username, password, first_name, last_name, roles: list[str]):
    url = f'{BASE_URL}/api/register'
    myobj = {
        "id": user_id,
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "roles": roles
    }
    response = requests.post(url, json = myobj)
    return response.status_code == 201 or response.status_code == 200

def user_login(username, password):
    url = f'{BASE_URL}/api/login'
    myobj = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json = myobj)
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            return data["access_token"]
    
    return None

def create_class(dept_code, course_num, section_no, academic_year, semester,
                instructor_id, room_capacity, 
                course_start_date, enrollment_start, enrollment_end, access_token):
    # Prepare header & message body        
    headers = {
        "Content-Type": "application/json;",
        "Authorization": f"Bearer {access_token}"
    }
    body = {
        "dept_code": dept_code,
        "course_num": course_num,
        "section_no": section_no,
        "academic_year": academic_year,
        "semester": semester,
        "instructor_id": instructor_id,
        "room_num": 205,
        "room_capacity": room_capacity,
        "course_start_date": course_start_date,
        "enrollment_start": enrollment_start,
        "enrollment_end": enrollment_end
    }

    # Send request
    url = f'{BASE_URL}/api/classes/'
    response = requests.post(url, headers=headers, json=body)
    return response

def enroll_class(class_id, access_token):
    # Prepare header & message body
    headers = {
        "Content-Type": "application/json;",
        "Authorization": f"Bearer {access_token}"
    }
    body = {
        "class_id": class_id
    }

    # Send request
    url = f'{BASE_URL}/api/enrollment/'
    response = requests.post(url, headers=headers, json=body)
    return response
