import os.path
from datetime import datetime
from pkg_resources import resource_filename
from jinja2 import Environment, PackageLoader
import pymongo
from eduid_actions.action_abc import ActionPlugin
from eduid_am.db import MongoDB


PACKAGE_NAME = 'eduid_action.tou'


env = Environment(loader=PackageLoader(PACKAGE_NAME, 'templates'))


class ToUPlugin(ActionPlugin):

    steps = 1
    translations = {}

    @classmethod
    def get_translations(cls):
        return cls.translations

    def inludeme(self, config):
        settings = config.registry.settings
        mongo_replicaset = settings.get('mongo_replicaset', None)
        if mongo_replicaset is not None:
            mongodb = MongoDB(db_uri=settings['mongo_uri_tou'],
                              replicaSet=mongo_replicaset)
        else:
            mongodb = MongoDB(db_uri=settings['mongo_uri_tou'])
        tou_db = mongodb.get_database()
        config.set_request_property(tou_db, 'tou_db', reify=True)


    def get_number_of_steps(self):
        return self.steps

    def get_action_body_for_step(self, step_number, action, request, errors=None):
        version = action['params']['version']
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
        userid = action['user_oid']
        version = action['params']['version']
        try:
            tous_accepted = request.tou_db.tous_accepted
        except pymongo.errors.ConnectionFailure:
            msg = _(u'Error connecting to the database')
            raise self.ActionError(msg)
        new_acceptance = {'version': version,
                          'ts': datetime.now()}
        previous = tous_accepted.find_one({'user_oid': userid})
        if previous is not None:
            versions = previous['versions']
            versions.append(new_acceptance)
            tous_accepted.find_and_modify(
                    {'user_oid': userid},
                    {'$set': {'versions': versions}})
        else:
            new_doc = {'user_oid': userid,
                       'versions': [new_acceptance]}
            tous_accepted.insert(new_doc)

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
