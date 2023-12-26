import unittest
from flask_testing import TestCase
from gamedis.models import User
from gamedis import createApp, db
from gamedis import models
import urllib


class AccountTestCase(TestCase):

    def assertRedirects(self, response, location, message=None):  # override
        """
        [OVERRIDE]
        Checks if response is an HTTP redirect to the
        given location.

        :param response: Flask response
        :param location: relative URL path to SERVER_NAME or an absolute URL
        """
        parts = urllib.parse.urlparse(location)

        if parts.netloc:
            expected_location = location
        else:
            server_name = self.app.config.get('SERVER_NAME') or 'localhost'
            expected_location = urllib.parse.urljoin(
                "http://%s" % server_name, location)

        valid_status_codes = (301, 302, 303, 305, 307, 200)
        valid_status_code_str = ', '.join(
            str(code) for code in valid_status_codes)
        not_redirect = "HTTP Status %s expected but got %d" % (
            valid_status_code_str, response.status_code)
        self.assertTrue(response.status_code in valid_status_codes,
                        message or not_redirect)
        self.assertEqual(response.location, expected_location, message)

    def create_app(self):
        PORT = 5500
        DOMAIN = f"localhost:{PORT}"
        app = createApp()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'gamedis_secret'
        app.config['SERVER_NAME'] = [DOMAIN]
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()
        # Create a test user
        test_user = User(uname='test_user',
                         password='test_password', alias='Test User')
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        response = self.client.post('/iden-operation/login', data=dict(
            name='test_user',
            password='test_password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/account/my-account')
        # self.assert_template_used('account.html')

    # def test_failed_login(self):
    #     response = self.client.post('/iden-operation/login', data=dict(
    #         name='test_user2',
    #         password='test_password2'
    #     ), follow_redirects=True)
    #     self.assertEqual(response.status_code, 401)

    # def test_signup(self):
    #     response = self.client.post('/iden-operation/signup', data=dict(
    #         inputUsername='new_user',
    #         inputPassword='new_password',
    #         inputPassword2='new_password'
    #     ), follow_redirects=True)
    #     self.assert200(response)
    #     self.assertIn(b'Your account has been created!', response.data)
    #     # Ensure the new user exists in the database
    #     new_user = User.query.filter_by(uname='new_user').first()
    #     self.assertIsNotNone(new_user)
    #     self.assertEqual(new_user.alias, 'new_user')

    # # Add more test methods as needed to cover different functionalities


if __name__ == '__main__':
    unittest.main()
