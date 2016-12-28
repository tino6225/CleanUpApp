# For Google App Engine local unit testing
import sys
sys.path.insert(1, './lib')

import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from mobileWeb import app
from model import Location, Photo, UserAccount
import urllib2
import json
from flask_webtest import TestApp
from flask import Flask
from flask_testing import TestCase

class BaseTest(TestCase):
    render_templates = False

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testapp = TestApp(self.app)
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def getFlashMessage(self, response):
        if response.flashes:
            return response.flashes[0][1]
        else:
            return None


class TestTemplates(BaseTest):

    def test_template_index(self):
        response = self.testapp.get("/")
        self.assert_template_used('index.html')

    def test_template_index2(self):
        response = self.testapp.get("/index")
        self.assert_template_used('index.html')

    def test_template_signup(self):
        response = self.testapp.get("/signup")
        self.assert_template_used('signup.html')

    def test_template_login(self):
        response = self.testapp.get("/login")
        self.assert_template_used('login.html')

    def test_template_image(self):
        response = self.testapp.get("/image")
        self.assert_template_used('image.html')

    def test_template_history(self):
        response = self.testapp.get("/history")
        self.assert_template_used('history.html')


class TestFlashMessages(BaseTest):

    def test_flash_index(self):
        response = self.testapp.get("/")
        self.assert_message_flashed('')

    def test_flash_index2(self):
        response = self.testapp.get("/index")
        self.assert_message_flashed('')

    def test_flash_logout(self):
        response = self.testapp.get("/index")
        self.assert_message_flashed("No need to logout. You were not signed in")

    def test_flash_imageHistory(self):
        response = self.testapp.get("/imageHistory")
        self.assert_message_flashed("You are not logged in.  Please login to view your image records.")

    def test_flash_apiAddRecordNotLoggedIn(self):
        response = self.testapp.post_json("/apiAddRecord", dict(coordinates='123456',
            comments='test comment', zipCode='12345'))
        self.assert_message_flashed("You are not logged in.  Please login to save report.")

class DatastoreTestCase(BaseTest):

    def createAccount(self):
        return self.testapp.post('/signup', {'username': 'user',
            'password': 'password',
            'email': 'email@email.com'})

    def logout(self):
        return self.testapp.get('/logout')

    def login(self):
        return self.testapp.post('/login', {'username': 'user',
            'password': 'password'})

    def testAccountCreation(self):
        self.createAccount()
        q = UserAccount.query(UserAccount.username == 'user')
        self.assertEqual(q.get().username, 'user')

    def testAccountCreationAlreadyLoggedIn(self):
        self.createAccount()
        response = self.login()
        self.assertEqual(self.getFlashMessage(response), "Already logged in as 'user'")

    def testAccountLoginLogout(self):
        self.createAccount()
        response = self.logout()
        self.assertEqual(self.getFlashMessage(response), 'user is now logged off')

    def testAccountLoginAlreadyLoggedOut(self):
        self.createAccount()
        self.logout()
        response = self.logout()
        self.assertEqual(self.getFlashMessage(response), 'No need to logout. You were not signed in')

    def testAccountLoginLogoutLogin(self):
        self.createAccount()
        self.logout()
        response = self.login()
        self.assertEqual(self.getFlashMessage(response), " You are logged on. Your user key is 'user'.")

    def test_flash_apiAddRecordLoggedIn(self):
        self.createAccount()
        response = self.testapp.post_json("/apiAddRecord", dict(coordinates='123456',
            comments='test comment', zipCode='12345'))
        parsed_json = json.loads(response.body)
        self.assertEqual(parsed_json.keys(), [u'Please upload an image next. This record ID is'])
        self.assertEqual(parsed_json['Please upload an image next. This record ID is'], 1)

if __name__ == '__main__':
    unittest.main()
