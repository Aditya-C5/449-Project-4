import unittest
import requests
from tests.helpers import user_register, user_login, unittest_setUp, unittest_tearDown
from tests.settings import BASE_URL, USER_DB_PATH

class UserServiceTest(unittest.TestCase):
    def setUp(self):
        unittest_setUp()
    
    def tearDown(self):
        unittest_tearDown()

    # ------------- REGISTER TESTS -------------
    def test_register(self):
        result = user_register(2, "nathan", "1234", "nathan", "nguyen", ["Student"])
        self.assertTrue(result)

    def test_register_duplicate_username(self):
        user_register(2, "nathan", "1234", "nathan", "nguyen", ["Student"])
        result = user_register(2, "nathan", "1234", "nathan", "nguyen", ["Student"])
        self.assertFalse(result)

    # ------------- LOGIN TESTS -------------
    def test_login(self):
        user_register(2, "nathan", "1234", "nathan", "nguyen", ["Student"])
        access_token = user_login(username="nathan", password="1234")
        self.assertIsNotNone(access_token)

    def test_login_wrong_password(self):
        user_register(2, "nathan", "1234", "nathan", "nguyen", ["Student"])
        access_token = user_login(username="nathan", password="wrong_password")
        self.assertIsNone(access_token)

    def test_login_wrong_username(self):
        access_token = user_login(username="username_does_not_exists", password="1234")
        self.assertIsNone(access_token)   

if __name__ == '__main__':
    unittest.main()