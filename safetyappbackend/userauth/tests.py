# Create your tests here.
import pytest
from faker import Faker
from rest_framework.test import APIClient


class TestUserAuthViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.faker = Faker()
        self.status_code_ok = 200
        self.status_code_created = 201
        self.status_code_bad_request = 400

        self.login_url = "/userauth/api/auth/loginview/"
        self.signup_url = "/userauth/api/auth/signupview/"

    @pytest.mark.django_db
    def test_signupview_success(self):
        data = {
            "phone_number": str(self.faker.random_number(digits=10, fix_len=True)),
            "password": "TestPassword123",
        }
        response = self.client.post(self.signup_url, data, format="json")

        assert response.status_code == self.status_code_ok
        assert "access_token" in response.data
        assert "user" in response.data
        assert "status" in response.data
        assert response.data["status"] == self.status_code_created

    @pytest.mark.django_db
    def test_signupview_user_already_registered(self):
        data = {
            "phone_number": str(self.faker.random_number(digits=10, fix_len=True)),
            "password": "TestPassword123",
        }

        self.client.post(self.signup_url, data, format="json")

        response = self.client.post(self.signup_url, data, format="json")

        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["msg"]["phone_number"][0]
            == "Phone number already registered."
        )

    def test_signupview_without_phonenumber(self, db):
        data = {
            "phone_number": "",
            "password": "TestPassword123",
        }
        response = self.client.post(self.signup_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert response.data["msg"]["phone_number"][0] == "This field may not be blank."

    def test_signupview_without_password(self, db):
        data = {
            "phone_number": str(self.faker.random_number(digits=10, fix_len=True)),
            "password": "",
        }
        response = self.client.post(self.signup_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert response.data["msg"]["password"][0] == "This field may not be blank."

    def test_signupview_password_length(self, db):
        data = {
            "phone_number": str(self.faker.random_number(digits=10, fix_len=True)),
            "password": "123456",
        }
        response = self.client.post(self.signup_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["msg"]["password"][0]
            == "Ensure this field has at least 8 characters."
        )

    def test_signupview_phone_number_verification(self, db):
        data = {
            "phone_number": str(self.faker.random_number(digits=9, fix_len=True)),
            "password": "",
        }
        response = self.client.post(self.signup_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["msg"]["phone_number"][0]
            == "Ensure this field has at least 10 characters."
        )

    @pytest.mark.django_db
    def test_signupview_with_incorrect_phonenumber_format(self):
        data = {
            "phone_number": "12345ABCDM",
            "password": "TestPassword123",
        }
        response = self.client.post(self.signup_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["msg"]["phone_number"][0]
            == "Phone number must contain only digits."
        )

    # Login View Tests
    def test_loginview_success(self, db):
        phone_number = str(self.faker.random_number(digits=10, fix_len=True))
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_ok
        assert "access_token" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

    def test_loginview_with_incorrect_password(self, db):
        phone_number = str(self.faker.random_number(digits=10, fix_len=True))
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": phone_number,
            "password": "TestPassword1234",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert response.data["error"]["non_field_errors"][0] == "Incorrect password."

    def test_loginview_with_incorrect_password_length(self, db):
        phone_number = str(self.faker.random_number(digits=10, fix_len=True))
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": phone_number,
            "password": "TestP",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["error"]["password"][0]
            == "Ensure this field has at least 8 characters."
        )

    def test_loginview_with_incorrect_phonenumber(self, db):
        phone_number = str(self.faker.random_number(digits=10, fix_len=True))
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": str(self.faker.random_number(digits=10, fix_len=True)),
            "password": "TestPassword1234",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert response.data["error"]["non_field_errors"][0] == "User not found."

    def test_loginview_phonenumber_incorrect_length(self, db):
        phone_number = str(self.faker.random_number(digits=10, fix_len=True))
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": str(self.faker.random_number(digits=9, fix_len=True)),
            "password": "TestPassword1234",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["error"]["phone_number"][0]
            == "Ensure this field has at least 10 characters."
        )

    def test_loginview_phonenumber_incorrect_formate_verification(self, db):
        phone_number = "231234ABCD"
        signup_data = {
            "phone_number": phone_number,
            "password": "TestPassword123",
        }
        self.client.post(self.signup_url, signup_data, format="json")

        login_data = {
            "phone_number": phone_number,
            "password": "TestPassword1234",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["error"]["phone_number"][0]
            == "Phone number must contain only digits."
        )

    def test_loginview_missing_fields(self, db):
        data = {
            "phone_number": "",
            "password": "",
        }
        response = self.client.post(self.login_url, data, format="json")
        assert response.status_code == self.status_code_bad_request
        assert (
            response.data["error"]["phone_number"][0] == "This field may not be blank."
        )
        assert response.data["error"]["password"][0] == "This field may not be blank."
