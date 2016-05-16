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


import os.path
from bson import ObjectId
from datetime import datetime
from pkg_resources import resource_filename
from jinja2 import Environment, PackageLoader
from pyramid.httpexceptions import HTTPInternalServerError
from eduid_actions.action_abc import ActionPlugin
from eduid_userdb import MongoDB
from eduid_userdb.tou import ToUEvent
from eduid_userdb.actions.tou import ToUUserDB, ToUUser
from eduid_am.tasks import update_attributes_keep_result

import logging
logger = logging.getLogger(__name__)


PACKAGE_NAME = 'eduid_action.tou'


env = Environment(loader=PackageLoader(PACKAGE_NAME, 'templates'))


class ToUPlugin(ActionPlugin):

    steps = 1
    translations = {}

    @classmethod
    def get_translations(cls):
        return cls.translations

    @classmethod
    def includeme(self, config):
        settings = config.registry.settings
        mongodb = MongoDB(db_uri=settings['mongo_uri'], db_name='eduid_actions')
        tou_db = mongodb.get_database('eduid_tou')
        config.set_request_property(tou_db, 'tou_db_legacy', reify=True)

        tou_db = ToUUserDB(settings['mongo_uri'])
        config.registry.settings['tou_db'] = tou_db
        config.set_request_property(lambda x: x.registry.settings['tou_db'], 'tou_db', reify=True)

    def get_number_of_steps(self):
        return self.steps

    def get_action_body_for_step(self, step_number, action, request, errors=None):
        version = action.params['version']
        lang = self.get_language(request)
        text = self.get_tou_text(version, lang)
        text = text.decode('utf-8')
        _ = self.translations[lang].ugettext
        template = env.get_template('main.jinja2')
        return template.render(tou_text=text, _=_)

    def perform_action(self, action, request):
        _ = self.get_ugettext(request)
        if not request.POST.get('accept', ''):
            msg = _(u'You must accept the new terms of use to continue logging in')
            raise self.ActionError(msg)
        userid = action.user_id
        version = action.params['version']
        user = request.tou_db.get_user_by_id(userid, raise_on_missing=False)
        logger.debug('Loaded ToUUser {!s} from db'.format(user))
        if not user:
            user = ToUUser(userid=userid, tou=[])
        user.tou.add(ToUEvent(
            version = version,
            application = 'eduid_tou_plugin',
            created_ts = datetime.utcnow(),
            event_id = ObjectId()
            ))
        request.tou_db.save(user)
        logger.debug("Asking for sync of {!s} by Attribute Manager".format(user))
        rtask = update_attributes_keep_result.delay('tou', str(user.user_id))
        try:
            result = rtask.get(timeout=10)
            logger.debug("Attribute Manager sync result: {!r}".format(result))
        except Exception, e:
            logger.exception("Failed Attribute Manager sync request: " + str(e))
            message = _('There were problems with your submission. '
                        'You may want to try again later, '
                        'or contact the site administrators.')
            request.session.flash(message)
            raise HTTPInternalServerError()

    def get_tou_text(self, version, lang):
        versions_path = resource_filename(PACKAGE_NAME, 'versions')
        lang_path = os.path.join(versions_path, lang)
        _ = self.translations[lang].ugettext
        if not os.path.isdir(lang_path):
            msg = _(u'Missing language for ToU versions: {0}')
            raise self.ActionError(msg.format(lang), rm=True)
        version_path = os.path.join(lang_path, version + '.txt')
        if not os.path.exists(version_path):
            msg = _(u'Missing text for ToU version {0} and lang {1}')
            raise self.ActionError(msg.format(version, lang), rm=True)
        with open(version_path) as f:
            return f.read()
