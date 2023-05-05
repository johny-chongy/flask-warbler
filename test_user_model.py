"""User model tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow, DEFAULT_IMAGE_URL

from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does the user have 0 messages and 0 followers?"""

        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_is_following(self):
        """Is user 1 following user 2?"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u2.followers.append(u1)

        self.assertEqual(u1.is_following(u2), True)

    def test_is_not_following(self):
        """Is user 1 not following user 2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_following(u2), False)


    def test_is_followed_by(self):
        """Is user 2 followed by user 1?"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u2.followers.append(u1)

        self.assertEqual(u2.is_followed_by(u1), True)

    def test_is_not_followed_by(self):
        """Is user 2 not followed by user 1?"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u2.is_followed_by(u1), False)

    def test_user_signup_success(self):
        """
        Does the User signup successfully create a new user given
        valid credentials?
        """

        user = User.signup("user_success",
                           "user_success@email.com",
                           "password",
                           None)
        db.session.commit()

        self.assertEqual(user.username, "user_success")
        self.assertEqual(user.email, "user_success@email.com")
        self.assertEqual(user.image_url, DEFAULT_IMAGE_URL)
        self.assertTrue(user.password.startswith("$2b$12$"))

    def test_user_signup_fail(self):
        """
        Does the User signup successfully create a new user given
        valid credentials?
        """

        user = User.signup("u2", "u2@email.com", "password", None)

        self.assertRaises(IntegrityError, db.session.commit)

    def test_successful_authenticate(self):
        """
        Does User.authenticate return a user with valid
        username and id?
        """
        u1 = User.query.get(self.u1_id)

        self.assertEqual(User.authenticate("u1","password"), u1)

    def test_invalid_username_authenticate(self):
        """
        Does User.authenticate return false with a invalid
        username input?
        """

        self.assertFalse(User.authenticate("wrongusername","password"))

    def test_invalid_password_authenticate(self):
        """
        Does User.authenticate return false with a invalid
        password input?
        """

        self.assertFalse(User.authenticate("u1","wrongpassword"))