#
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
from bson import ObjectId
from datetime import datetime

import urllib3
from flask import current_app, request, abort

from eduid_webapp.actions.action_abc import ActionPlugin
from eduid_userdb.tou import ToUEvent
from eduid_userdb.actions.tou import ToUUserDB, ToUUser
from eduid_am.tasks import update_attributes_keep_result


PACKAGE_NAME = 'eduid_action.tou'

http = urllib3.PoolManager()


class ToUPlugin(ActionPlugin):

    steps = 1

    @classmethod
    def includeme(self, app):
        app.tou_db = ToUUserDB(app.config.get('MONGO_URI'))

    def get_number_of_steps(self):
        return self.steps

    def get_url_for_bundle(self, action):
        base = current_app.config.get('BUNDLES_URL')
        bundle_name = '{}.js'
        if current_app.config.get('DEBUG'):
            bundle_name = '{}-bundle.dev.js'
        url = '{}{}'.format(
                base,
                bundle_name.format(PACKAGE_NAME)
                )
        return url

    def get_config_for_bundle(self, action):
        url = current_app.config.get('INTERNAL_SIGNUP_URL')
        try:
            r = http.request('GET', url + 'services/signup/get-tous', retries=False)
            current_app.logger.debug('Response: {!r} with headers: '
                    '{!r}'.format(r, r.headers))
            if r.status == 302:
                headers = {'Cookie': r.headers.get('Set-Cookie')}
                current_app.logger.debug('Headers: {!r}'.format(headers))
                r = http.request('GET', url + 'services/signup/get-tous',
                                 retries=False, headers=headers)
                current_app.logger.debug('2nd response: {!r} with headers: '
                        '{!r}'.format(r, r.headers))
        except Exception as e:
            current_app.logger.debug('Problem getting config: {!r}'.format(e))
            raise self.ActionError('tou.no-tou')
        if r.status != 200:
            current_app.logger.debug('Problem getting config, '
                                     'response status: {!r}'.format(r.status))
            raise self.ActionError('tou.no-tou')
        return {
            'version': action.params['version'],
            'tous': json.loads(r.data)['payload'],
            'available_languages': current_app.config.get('AVAILABLE_LANGUAGES')
            }


    def perform_step(self, action):
        if not request.get_json().get('accept', ''):
            raise self.ActionError('tou.must-accept')
        userid = action.user_id
        version = action.params['version']
        user = current_app.tou_db.get_user_by_id(userid, raise_on_missing=False)
        current_app.logger.debug('Loaded ToUUser {} from db'.format(user))
        if not user:
            user = ToUUser(userid=userid, tou=[])
        event_id = ObjectId()
        user.tou.add(ToUEvent(
            version = version,
            application = 'eduid_tou_plugin',
            created_ts = datetime.utcnow(),
            event_id = event_id
            ))
        current_app.tou_db.save(user)
        current_app.logger.debug("Asking for sync of {} by Attribute Manager".format(user))
        rtask = update_attributes_keep_result.delay('tou', str(userid))
        try:
            result = rtask.get(timeout=10)
            current_app.logger.debug("Attribute Manager sync result: {!r}".format(result))
            return {}
        except Exception as e:
            current_app.logger.error("Failed Attribute Manager sync request: " + str(e))
            user.tou.remove(event_id)
            current_app.tou_db.save(user)
            raise self.ActionError('tou.sync-problem')
