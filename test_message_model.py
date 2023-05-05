"""Message model tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_model.py


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


class MessageModelTestCase(TestCase):
    def setUp(self):
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_create_successful_message(self):
        """
        Testing if a message is successfully added to u1's messages
        with valid inputs
        """

        u1 = User.query.get(self.u1_id)
        u1_first_message = Message(text="hello", user_id=self.u1_id)

        db.session.add(u1_first_message)
        db.session.commit()

        self.assertIn(u1_first_message, u1.messages)

    def test_liking_message(self):
        """
        Testing that liking message adds message to user's liked_messages
        """

        u2 = User.query.get(self.u2_id)
        u1_message = Message(text="first like", user_id=self.u1_id)

        db.session.add(u1_message)
        db.session.commit()

        u2.liked_messages.append(u1_message)

        self.assertIn(u1_message, u2.liked_messages)
        self.assertEqual(len(u1_message.likes), 1)

    def test_unliking_message(self):
        """
        Testing that unliking message removes message from user's liked_messages
        """

        u2 = User.query.get(self.u2_id)
        u1_message = Message(text="first like", user_id=self.u1_id)

        db.session.add(u1_message)
        db.session.commit()

        u2.liked_messages.append(u1_message)
        u2.liked_messages.remove(u1_message)

        self.assertNotIn(u1_message, u2.liked_messages)
        self.assertEqual(len(u1_message.likes), 0)