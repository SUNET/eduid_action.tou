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

from bson import ObjectId
from datetime import datetime

from flask import current_app, request, abort

from eduid_actions.action_abc import ActionPlugin
from eduid_userdb.tou import ToUEvent
from eduid_userdb.actions.tou import ToUUserDB, ToUUser
from eduid_am.tasks import update_attributes_keep_result


PACKAGE_NAME = 'eduid_action.tou'


class ToUPlugin(ActionPlugin):

    steps = 1

    @classmethod
    def includeme(self, app, config):
        app.tou_db = ToUUserDB(config.get('MONGO_URI'))

    def get_number_of_steps(self):
        return self.steps

    def get_url_for_bundle(self, action):
        version = action.params['version']
        base = current_app.config.get('BUNDLES_URL')
        bundle_name = '{}.js'
        if current_app.config.get('DEBUG'):
            bundle_name = '{}-dev.js'
        url = '{}{}?version={}'.format(
                base,
                bundle_name.format(PACKAGE_NAME),
                version
                )
        return url


    def perform_action(self, action):
        if not request.args.get('accept', ''):
            raise self.ActionError('tou.must-accept')
        userid = action.user_id
        version = action.params['version']
        user = current_app.tou_db.get_user_by_id(userid, raise_on_missing=False)
        current_app.logger.debug('Loaded ToUUser {} from db'.format(user))
        if not user:
            user = ToUUser(userid=userid, tou=[])
        user.tou.add(ToUEvent(
            version = version,
            application = 'eduid_tou_plugin',
            created_ts = datetime.utcnow(),
            event_id = ObjectId()
            ))
        current_app.tou_db.save(user)
        current_app.logger.debug("Asking for sync of {} by Attribute Manager".format(user))
        rtask = update_attributes_keep_result.delay('tou', str(userid))
        try:
            result = rtask.get(timeout=10)
            current_app.logger.debug("Attribute Manager sync result: {!r}".format(result))
        except Exception as e:
            current_app.logger.error("Failed Attribute Manager sync request: " + str(e))
            abort(500)
