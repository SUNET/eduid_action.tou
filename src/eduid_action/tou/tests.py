# -*- coding: utf8 -*-

from datetime import datetime
from bson import ObjectId
from copy import deepcopy
import pymongo
from eduid_userdb.db import MongoDB
from eduid_userdb.signup import SignupUser
from eduid_userdb.userdb import User
from eduid_userdb.testing import MOCKED_USER_STANDARD
from eduid_actions.testing import FunctionalTestCase


TOU_ACTION = {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('012345678901234567890123'),
        'action': 'tou',
        'preference': 100,
        'params': {
            'version': 'test-version'
            }
        }


class ToUActionTests(FunctionalTestCase):

    def setUp(self):
        extra_settings = {
                'mongo_name_tou': 'eduid_tou_testing',
                'mongo_name_signup': 'eduid_signup_testing',
                }
        extra_dbs = [
                ('mongo_uri_tou', 'eduid_tou_testing'),
                ('mongo_uri_signup', 'eduid_signup_testing'),
                ]
        super(ToUActionTests, self).setUp(extra_settings, extra_dbs)
        mongodb = MongoDB(self.settings['mongo_uri_tou'])
        self.tou_db = mongodb.get_database('eduid_tou_testing')
        self.signup_db = self.testapp.app.registry.settings['signup_db']
        user_data = deepcopy(MOCKED_USER_STANDARD)
        user_data['modified_ts'] = datetime.utcnow()
        self.amdb.save(User(data=user_data), check_sync=False)
        self.signup_db.save(SignupUser(data=user_data), check_sync=False)

    def tearDown(self):
        self.tou_db.tous_accepted.drop()
        self.amdb._drop_whole_collection()
        self.signup_db._drop_whole_collection()
        super(ToUActionTests, self).tearDown()


    def test_action_success(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=012345678901234567890123'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.signup_db.get_user_by_id('012345678901234567890123')
        self.assertEqual(len(user.tou._elements), 1)

    def test_success_two_versions(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=012345678901234567890123'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.signup_db.get_user_by_id('012345678901234567890123')
        self.assertEqual(len(user.tou._elements), 1)
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'test-version-2'
        self.actions_db.add_action(data=action)
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        user = self.signup_db.get_user_by_id('012345678901234567890123')
        self.assertEqual(len(user.tou._elements), 1)
        res = form.submit('accept')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.signup_db.get_user_by_id('012345678901234567890123')
        self.assertEqual(len(user.tou._elements), 2)

    def test_action_success_change_lang(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=012345678901234567890123'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.testapp.get('/set_language/?lang=sv')
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        text = u'Test TöU Svenska'.encode('utf-8')
        self.assertIn(text, res.body)
        self.assertIn('acceptera', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.signup_db.get_user_by_id('012345678901234567890123')
        self.assertEqual(len(user.tou._elements), 1)

    def test_nonexistant_version(self):
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'wrong-version'
        self.actions_db.add_action(data=action)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=012345678901234567890123'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Missing text for ToU', res.body)
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)

    def test_action_reject(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=012345678901234567890123'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('reject')
        self.assertIn('you must accept the new terms of use', res.body)
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
