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
from mock import MagicMock
from datetime import datetime
from bson import ObjectId
from copy import deepcopy
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

    def test_get_action(self):
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
