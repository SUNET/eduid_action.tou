# -*- coding: utf8 -*-#

# Copyright (c) 2015 NORDUnet A/S
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#     3. Neither the name of the NORDUnet nor the names of its
#        contributors may be used to endorse or promote products derived
#        from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

__author__ = 'eperez'


from datetime import datetime
from bson import ObjectId
from copy import deepcopy
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


class ToUActionPluginTests(FunctionalTestCase):

    def setUp(self):
        super(ToUActionPluginTests, self).setUp()
        self.tou_db = self.testapp.app.registry.settings['tou_db']
        user_data = deepcopy(MOCKED_USER_STANDARD)
        user_data['modified_ts'] = datetime.utcnow()
        self.amdb.save(User(data=user_data), check_sync=False)
        self.test_user_id =  '012345678901234567890123'

    def tearDown(self):
        self.tou_db._drop_whole_collection()
        self.amdb._drop_whole_collection()
        super(ToUActionPluginTests, self).tearDown()


    def test_action_success(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid={!s}&token=abc&nonce=sdf&'
                'ts=1401093117'.format(self.test_user_id))
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        res.mustcontain('Test ToU English')
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.db_count(), 0)
        res = form.submit('accept')
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/perform-action')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.amdb.get_user_by_id(self.test_user_id)
        self.assertEqual(len(user.tou._elements), 1)

    def test_success_two_versions(self):
        self.test_action_success()
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'test-version-2'
        self.actions_db.add_action(data=action)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid={!s}&token=abc&nonce=sdf&'
                'ts=1401093117'.format(self.test_user_id))
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        res.mustcontain('Test ToU English')
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        user = self.amdb.get_user_by_id(self.test_user_id)
        self.assertEqual(len(user.tou._elements), 1)
        res = form.submit('accept')
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/perform-action')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.amdb.get_user_by_id(self.test_user_id)
        self.assertEqual(len(user.tou._elements), 2)

    def test_action_success_change_lang(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid={!s}&token=abc&nonce=sdf&'
                'ts=1401093117'.format(self.test_user_id))
        res = self.testapp.get(url)
        self.testapp.get('/set_language/?lang=sv')
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        res.mustcontain(u'Test TöU Svenska'.encode('utf-8'))
        res.mustcontain('acceptera')
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        user = self.amdb.get_user_by_id(self.test_user_id)
        self.assertEqual(len(user.tou._elements), 0)
        res = form.submit('accept')
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://localhost/perform-action')
        self.assertEqual(self.actions_db.db_count(), 0)
        user = self.amdb.get_user_by_id(self.test_user_id)
        self.assertEqual(len(user.tou._elements), 1)

    def test_nonexistant_version(self):
        action = deepcopy(TOU_ACTION)
        action['params']['version'] = 'wrong-version'
        self.actions_db.add_action(data=action)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid={!s}&token=abc&nonce=sdf&'
                'ts=1401093117'.format(self.test_user_id))
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(self.actions_db.db_count(), 1)
        res = self.testapp.get(res.location)
        res.mustcontain('Missing text for ToU')
        self.assertEqual(self.actions_db.db_count(), 0)
        self.assertEqual(self.tou_db.db_count(), 0)

    def test_action_reject(self):
        self.actions_db.add_action(data=TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid={!s}&token=abc&nonce=sdf&'
                'ts=1401093117'.format(self.test_user_id))
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        res.mustcontain('Test ToU English')
        form = res.forms['tou-form']
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.db_count(), 0)
        res = form.submit('reject')
        res.mustcontain('You must accept the new terms of use')
        self.assertEqual(self.actions_db.db_count(), 1)
        self.assertEqual(self.tou_db.db_count(), 0)
