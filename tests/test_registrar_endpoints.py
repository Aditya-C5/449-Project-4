import os
import unittest
import requests
from tests.helpers import *
from tests.settings import BASE_URL, USER_DB_PATH, ENROLLMENT_DB_PATH

class AutoEnrollmentTest(unittest.TestCase):
    def setUp(self):
        unittest_setUp()

    def tearDown(self):
        unittest_tearDown()

    def test_enable_auto_enrollment(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Prepare header & message body
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "enabled": True
        }

        # Send request
        url = f'{BASE_URL}/api/auto-enrollment/'
        response = requests.put(url, headers=headers, json=body)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.json())

    def test_disable_auto_enrollment(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Prepare header & message body
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "enabled": False
        }

        # Send request
        url = f'{BASE_URL}/api/auto-enrollment/'
        response = requests.put(url, headers=headers, json=body)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.json())


class CreateCourseTest(unittest.TestCase):
    def setUp(self):
        unittest_setUp()

    def tearDown(self):
        unittest_tearDown()

    def test_create_course(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Prepare header & message body
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "department_code": "CPSC",
            "course_no": 999,
            "title": "TEST TEST"
        }

        # Send request
        url = f'{BASE_URL}/api/courses/'
        response = requests.post(url, headers=headers, json=body)

        # Assert
        self.assertEqual(response.status_code, 200)
        # self.assertIn("detail", response.json())

    def test_create_duplicate_course(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Prepare header & message body
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "department_code": "CPSC",
            "course_no": 999,
            "title": "TEST TEST"
        }

        # Send request
        url = f'{BASE_URL}/api/courses/'
        response = requests.post(url, headers=headers, json=body)
        response = requests.post(url, headers=headers, json=body)

        # Assert
        self.assertEqual(response.status_code, 409)


class CreateClassTest(unittest.TestCase):
    def setUp(self):
        unittest_setUp()

    def tearDown(self):
        unittest_tearDown()

    def test_create_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Send request
        response = create_class("SOC", 301, 2, 2024, "FA", 1, 10,
                                "2023-06-12", "2023-06-01 09:00:00", "2024-06-15 17:00:00", access_token)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_create_duplicate_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Send request
        response = create_class("SOC", 301, 2, 2024, "FA", 1, 10,
                                "2023-06-12", "2023-06-01 09:00:00", "2024-06-15 17:00:00", access_token)

        response = create_class("SOC", 301, 2, 2024, "FA", 1, 10,
                                "2023-06-12", "2023-06-01 09:00:00", "2024-06-15 17:00:00", access_token)

        # Assert
        self.assertEqual(response.status_code, 409)

    def test_update_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Create a class
        response = create_class("SOC", 301, 2, 2024, "FA", 1, 10,
                                "2023-06-12", "2023-06-01 09:00:00", "2024-06-15 17:00:00", access_token)

        inserted_id = response.json()["inserted_id"]

        # Prepare header & message body        
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }
        body = {
            "instructor_id": 2
        }

        # Send request
        url = f'{BASE_URL}/api/classes/{inserted_id}'
        response = requests.patch(url, headers=headers, json=body)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_delete_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        # Send request
        response = create_class("SOC", 301, 2, 2024, "FA", 1, 10,
                                "2023-06-12", "2023-06-01 09:00:00", "2024-06-15 17:00:00", access_token)
        
        inserted_id = response.json()["inserted_id"]

        # Prepare header & message body        
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }

        # Send request
        url = f'{BASE_URL}/api/classes/{inserted_id}'
        response = requests.delete(url, headers=headers)
        
        # Assert
        self.assertEqual(response.status_code, 200)

    def test_delete_noexisting_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Student", "Registrar"])
        access_token = user_login("abc@csu.fullerton.edu", password="1234")

        inserted_id = 99999999

        # Prepare header & message body        
        headers = {
            "Content-Type": "application/json;",
            "Authorization": f"Bearer {access_token}"
        }

        # Send request
        url = f'{BASE_URL}/api/classes/{inserted_id}'
        response = requests.delete(url, headers=headers)
        
        # Assert
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()