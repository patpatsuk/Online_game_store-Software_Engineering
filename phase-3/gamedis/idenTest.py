import unittest
from flask_testing import TestCase
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from __init__ import createApp
from .models import User
from . import iden


class TestAuthentication(TestCase):

    def createApp(self):
        app = createApp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamedis_database.sqlite'
        app.register_blueprint(iden)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        # Create a test user
        test_user = User(uname='test_user',
                         password='hashed_password', alias='Test User')
        db.session.add(test_user)
        db.session.commit()

        # Make a test client
        response = self.client.post('/login', data=dict(
            inputUsername='test_user',
            inputPassword='password123'
        ), follow_redirects=True)

        # Check if the login is successful
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_user.uname, 'test_user')
        self.assertIn(b'Welcome, "test_user"!', response.data)

    def test_logout(self):
        # Log in a user
        with self.client:
            self.client.post('/login', data=dict(
                inputUsername='test_user',
                inputPassword='password123'
            ), follow_redirects=True)

            # Make a request to log out
            response = self.client.get('/logout', follow_redirects=True)

            # Check if the logout is successful
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(current_user.get_id())
            self.assertIn(b'Please login again!', response.data)

    def test_signup(self):
        # Make a test client
        response = self.client.post('/signup', data=dict(
            inputUsername='new_user',
            inputPassword='new_password',
            inputPassword2='new_password'
        ), follow_redirects=True)

        # Check if the signup is successful
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_user.uname, 'new_user')
        self.assertIn(b'Your account has been created!', response.data)


# if __name__ == '__main__':
idenT = unittest.main()
