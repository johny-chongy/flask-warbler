"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User, Follow

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)

        db.session.flush()
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id

        self.client = app.test_client()


class UserBaseFollowerViewTestCase(UserBaseViewTestCase):

    def test_see_follower_following_logged_in(self):
        """User 1 should be able to see that user 2 is following user 3."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            u3 = User.query.get(self.u3_id)

            u2_follow_u3 = Follow(user_being_followed_id=self.u3_id,
                                      user_following_id=self.u2_id)

            db.session.add(u2_follow_u3)
            db.session.commit()

            resp = c.get(f"/users/{self.u2_id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"<p>@{u3.username}</p>", html)

    def test_see_follower_following_logged_out(self):
        with self.client as c:

            u2_follow_u3 = Follow(user_being_followed_id=self.u3_id,
                                      user_following_id=self.u2_id)

            db.session.add(u2_follow_u3)
            db.session.commit()

            resp = c.get(f"/users/{self.u2_id}/following",
                         follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)
            self.assertIn("Sign up", html)

"""TODO: check for when user is not following (logged in and logged out)"""
"""TODO: check for followers endpoint"""
"""TODO: CHECK EVERY ENDPOINT"""

# TODO: MAKE A SETUP FOR LIKES

class UserLikesViewTestCase(UserBaseViewTestCase):
    def test_see_user_likes_logged_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            u2 = User.query.get(self.u2_id)
            u1_message = Message(text="first like", user_id=self.u1_id)

            db.session.add(u1_message)
            db.session.commit()

            u2.liked_messages.append(u1_message)

            resp = c.get(f"/users/{u2.id}/likes")

            html = resp.get_data(as_text=True)

            self.assertIn("first like", html)

    def test_see_user_likes_not_logged_in(self):
        with self.client as c:

            u2 = User.query.get(self.u2_id)
            u1_message = Message(text="first like", user_id=self.u1_id)

            db.session.add(u1_message)
            db.session.commit()

            u2.liked_messages.append(u1_message)

            resp = c.get(f"/users/{u2.id}/likes",
                         follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized.", html)
