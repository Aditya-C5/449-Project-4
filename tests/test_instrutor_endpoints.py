import os
import unittest
import requests
from tests.helpers import *
from tests.settings import BASE_URL, USER_DB_PATH, ENROLLMENT_DB_PATH

class CurrentEnrollmentTest(unittest.TestCase):
    def setUp(self):
        unittest_setUp()

    def tearDown(self):
        unittest_tearDown()

    def test_get_current_enrollment_for_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Instructor"])
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
        url = f'{BASE_URL}/api/classes/2/students/'
        response = requests.get(url, headers=headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("students", response.json())

    def test_get_students_who_dropped_class(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Instructor"])
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
        url = f'{BASE_URL}/api/classes/2/droplist/'
        response = requests.get(url, headers=headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("students", response.json())

    def test_get_students_on_waitlist(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Instructor"])
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
        url = f'{BASE_URL}/api/classes/2/waitlist/'
        response = requests.get(url, headers=headers)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn("students", response.json())

    def test_drop_student_administratively(self):
        # Register & Login
        user_register(2, "abc@csu.fullerton.edu", "1234", "nathan",
                      "nguyen", ["Instructor"])
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
        url = f'{BASE_URL}/api/enrollment/2/12345678/administratively/'
        response1 = requests.delete(url, headers=headers)
        response2 = requests.delete(url, headers=headers)

        # Assert
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 404)


if __name__ == '__main__':
    unittest.main()