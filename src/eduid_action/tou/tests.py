# -*- coding: utf8 -*-

from bson import ObjectId
from copy import deepcopy
import pymongo
from eduid_am.db import MongoDB
from eduid_actions.testing import FunctionalTestCase


TOU_ACTION = {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('123467890123456789014567'),
        'action': 'tou',
        'preference': 100,
        'params': {
            'version': 'test-version'
            }
        }


class ToUActionTests(FunctionalTestCase):

    def setUp(self):
        super(ToUActionTests, self).setUp()
        mongo_uri_templ = 'mongodb://localhost:{0}/eduid_tou_test'
        mongo_uri = mongo_uri_templ.format(str(self.port))
        self.testapp.app.registry.settings['tou_mongo_uri'] = mongo_uri
        try:
            mongodb = MongoDB(mongo_uri)
        except pymongo.errors.ConnectionFailure:
            self.setup_temp_db()
            mongo_uri = mongo_uri_templ.format(str(self.port))
            self.testapp.app.registry.settings['tou_mongo_uri'] = mongo_uri
            mongodb = MongoDB(mongo_uri)
        self.tou_db = mongodb.get_database()

    def tearDown(self):
        self.tou_db.tous_accepted.drop()
        super(ToUActionTests, self).tearDown()

    def test_action_success(self):
        self.db.actions.insert(TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.db.actions.find({}).count(), 0)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 1)

    def test_success_two_versions(self):
        self.db.actions.insert(TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.db.actions.find({}).count(), 0)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 1)
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'test-version-2'
        self.db.actions.insert(action)
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 1)
        res = form.submit('accept')
        self.assertEqual(self.db.actions.find({}).count(), 0)
        accepted = self.tou_db.tous_accepted.find({})
        self.assertEqual(accepted.count(), 1)
        self.assertEqual(len(accepted[0]['versions']), 2)

    def test_action_success_change_lang(self):
        self.db.actions.insert(TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.testapp.get('/set_language/?lang=sv')
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        text = u'Test TöU Svenska'.encode('utf-8')
        self.assertIn(text, res.body)
        self.assertIn('acceptera', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('accept')
        self.assertEqual(self.db.actions.find({}).count(), 0)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 1)

    def test_nonexistant_version(self):
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'wrong-version'
        self.db.actions.insert(action)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Missing text for ToU', res.body)
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)

    def test_action_reject(self):
        self.db.actions.insert(TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        self.assertIn('Test ToU English', res.body)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
        res = form.submit('reject')
        self.assertIn('you must accept the new terms of use', res.body)
        self.assertEqual(self.db.actions.find({}).count(), 1)
        self.assertEqual(self.tou_db.tous_accepted.find({}).count(), 0)
