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


import json
from mock import MagicMock, patch
from datetime import datetime
from bson import ObjectId
from copy import deepcopy
from flask import Response
from eduid_userdb.tou import ToUEvent
from eduid_webapp.actions.testing import ActionsTestCase
from eduid_action.tou.action import ToUPlugin
from eduid_action.tou.idp import add_tou_actions


TOU_ACTION = {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('012345678901234567890123'),
        'action': 'tou',
        'preference': 100,
        'params': {
            'version': 'test-version'
            }
        }

class MockIdPApp:

    class Config:
        def __init__(self, version):
            self.tou_version = version

    class Logger:
        debug = MagicMock()
        warning = MagicMock()

    def __init__(self, actions_db, version):
        self.config = self.Config(version)
        self.logger = self.Logger()
        self.actions_db = actions_db


class ToUActionPluginTests(ActionsTestCase):

    def setUp(self):
        super(ToUActionPluginTests, self).setUp()
        self.tou_db = self.app.tou_db

    def tearDown(self):
        self.tou_db._drop_whole_collection()
        super(ToUActionPluginTests, self).tearDown()

    def update_actions_config(self, config):
        config['INTERNAL_SIGNUP_URL'] = 'http://example.com/signup'
        return config

    def _prepare(self, session, **kwargs):
        self.prepare_session(session, plugin_name='tou',
                plugin_class=ToUPlugin, **kwargs)

    def tou_accepted(self, version):
        event_id = ObjectId()
        self.user.tou.add(ToUEvent(
            version = version,
            application = 'eduid_tou_plugin',
            created_ts = datetime.utcnow(),
            event_id = event_id
            ))
        self.app.central_userdb.save(self.user, check_sync=False)

    def test_get_tou_action(self):
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                with self.app.test_request_context():
                    mock_idp_app = MockIdPApp(self.app.actions_db, 'test-version')
                    add_tou_actions(mock_idp_app, self.user, None)
                    self.authenticate(client, sess)
                    response = client.get('/get-actions')
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertEquals(data['action'], True)
                    self.assertEquals(data['url'], 
                            'http://example.com/bundles/eduid_action.tou-bundle.dev.js')

    def test_get_tou_action_tou_accepted(self):
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                with self.app.test_request_context():
                    mock_idp_app = MockIdPApp(self.app.actions_db, 'test-version')
                    self.tou_accepted('test-version')
                    add_tou_actions(mock_idp_app, self.user, None)
                    self.authenticate(client, sess)
                    response = client.get('/get-actions')
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertEquals(data['action'], False)

    @patch('eduid_action.tou.action.http.request')
    def test_get_config(self, mock_http_request):
        data = json.dumps({'payload':{
                               'en': 'testing the ToU',
                               'sv': 'testa ToU'}
                               })
        resp = Response(response=data, status=200, mimetype='application/json')
        mock_http_request.return_value = resp
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                with self.app.test_request_context():
                    mock_idp_app = MockIdPApp(self.app.actions_db, 'test-version')
                    add_tou_actions(mock_idp_app, self.user, None)
                    self.authenticate(client, sess)
                    response = client.get('/get-actions')
                    self.assertEqual(response.status_code, 200)
                    response = client.get('/config')
                    data = json.loads(response.data)
                    self.assertEquals(data['payload']['tous']['sv'], 'testa ToU')

    @patch('eduid_action.tou.action.http.request')
    def test_get_config_302_tous(self, mock_http_request):
        resp = Response(status=302, mimetype='application/json')
        mock_http_request.return_value = resp
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                with self.app.test_request_context():
                    mock_idp_app = MockIdPApp(self.app.actions_db, 'test-version')
                    add_tou_actions(mock_idp_app, self.user, None)
                    self.authenticate(client, sess)
                    response = client.get('/get-actions')
                    self.assertEqual(response.status_code, 200)
                    response = client.get('/config')
                    data = json.loads(response.data)
                    self.assertEquals(data['payload']['message'], 'tou.no-tou')

    @patch('eduid_action.tou.action.http.request')
    def test_get_config_500_tous(self, mock_http_request):
        resp = Response(status=500, mimetype='application/json')
        mock_http_request.return_value = resp
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                with self.app.test_request_context():
                    mock_idp_app = MockIdPApp(self.app.actions_db, 'test-version')
                    add_tou_actions(mock_idp_app, self.user, None)
                    self.authenticate(client, sess)
                    response = client.get('/get-actions')
                    self.assertEqual(response.status_code, 200)
                    response = client.get('/config')
                    data = json.loads(response.data)
                    self.assertEquals(data['payload']['message'], 'tou.no-tou')

    @patch('eduid_action.tou.action.update_attributes_keep_result.delay')
    def test_get_accept_tou(self, mock_update):
        class RTask:
            def get(self, *args, **kwargs):
                return True
        mock_update.return_value = RTask()
        with self.session_cookie(self.browser) as client:
            with client.session_transaction() as sess:
                self._prepare(sess, action_dict=TOU_ACTION)
                with self.app.test_request_context():
                    csrf_token = sess.get_csrf_token()
                    data = json.dumps({'accept': True,
                                       'csrf_token': csrf_token})
                    response = client.post('/post-action', data=data,
                            content_type=self.content_type_json)
                    self.assertEquals(response.status_code, 200)

