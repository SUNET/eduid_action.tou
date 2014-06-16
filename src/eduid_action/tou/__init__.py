from pkg_resources import resource_filename
from jinja2 import Environment, PackageLoader
from eduid_actions.action_abc import ActionPlugin


PACKAGE_NAME = 'eduid_action.tou'


env = Environment(loader=PackageLoader(PACKAGE_NAME, 'templates'))


class ToUPlugin(ActionPlugin):

    steps = 1
    translations = {}

    @classmethod
    def get_translations(cls):
        return cls.translations

    def get_number_of_steps(self):
        return self.steps

    def get_action_body_for_step(self, step_number, action, request):
        version = action['params']['version']
        lang = self.get_language(request)
        text = self.get_tou_text(version, lang)
        _ = self.translations[lang].ugettext
        template = env.get_template('main.jinja2')
        return template.render(tou_text=text, _=_)

    def perform_action(self, action, request):
        if request.POST.get('accept', ''):
            return
        msg = _('you must accept the new terms of use to continue logging in')
        raise self.ActionError(msg)

    def get_tou_text(self, version, lang):
        pass
