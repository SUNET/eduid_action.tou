import os.path
from bson import ObjectId
from datetime import datetime
from pkg_resources import resource_filename
from jinja2 import Environment, PackageLoader
import pymongo
from eduid_actions.action_abc import ActionPlugin
<<<<<<< HEAD
from eduid_userdb import MongoDB
=======
from eduid_userdb.db import MongoDB
from eduid_userdb.tou import ToUEvent
from eduid_userdb.signup import SignupUserDB as UserDB
from eduid_am.tasks import update_attributes_keep_result

import logging
logger = logging.getLogger(__name__)
>>>>>>> new userdb


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
        tou_db = mongodb.get_database(settings['mongo_name_tou'])
        config.set_request_property(tou_db, 'tou_db', reify=True)

        signup_db = UserDB(settings['mongo_uri_signup'],
                            settings['mongo_name_signup'])
        config.registry.settings['signup_db'] = signup_db
        config.set_request_property(lambda x: x.registry.settings['signup_db'],
                'signup_db', reify=True)


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
            msg = _(u'you must accept the new terms of use to continue logging in')
            raise self.ActionError(msg)
        userid = action.user_id
        version = action.params['version']
        try:
            user = request.signup_db.get_user_by_id(userid)
        except pymongo.errors.ConnectionFailure:
            msg = _(u'Error connecting to the database')
            raise self.ActionError(msg)
        user.tou.add(ToUEvent(
            version = version,
            application = 'eduid_tou_plugin',
            created_ts = datetime.utcnow(),
            event_id = ObjectId()
            ))
        request.signup_db.save(user)
        logger.debug("Asking for sync of {!r} by Attribute Manager".format(
            str(user.user_id)))
        rtask = update_attributes_keep_result.delay('eduid_signup',
                str(user.user_id))
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
            raise self.ActionError(msg.format(lang))
        version_path = os.path.join(lang_path, version + '.txt')
        if not os.path.exists(version_path):
            msg = _(u'Missing text for ToU version {0} and lang {1}')
            raise self.ActionError(msg.format(version, lang))
        with open(version_path) as f:
            return f.read()


def add_tou_actions(idp_app, user, ticket):
    """
    Add an action requiring the user to accept a new version of the Terms of Use,
    in case the IdP configuration points to a version the user hasn't accepted.

    This function is called by the IdP when it iterates over all the registered
    action plugins entry points.

    :param idp_app: IdP application instance
    :param user: the authenticating user
    :param ticket: the SSO login data

    :type idp_app: eduid_idp.idp.IdPApplication
    :type user: eduid_idp.idp_user.IdPUser
    :type ticket: eduid_idp.login.SSOLoginData

    :return: None
    """
    version = idp_app.config.tou_version

    if user.tou.has_accepted(version):
        return

    if not idp_app.actions_db:
        return None

    if not idp_app.actions_db.has_actions(userid = str(user.user_id),
                                          action_type = 'accept_tou',
                                          params = {'version': version}):
        idp_app.actions_db.add_action(
            userid = str(user.user_id),
            action_type = 'accept_tou',
            preference = 100,
            params = {'version': version})
