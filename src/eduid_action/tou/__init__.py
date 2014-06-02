
from jinja2 import Environment, PackageLoader
from eduid_actions.action_abc import ActionPlugin


env = Environment(loader=PackageLoader('eduid_action.tou', 'templates'))


class ToUPlugin(ActionPlugin):

    steps = 1

    def get_number_of_steps(self):
        return self.steps

    def get_action_body_for_step(self, step_number, action, request):
        version = action['params']['version']
        text = self.get_tou_text(version)
        template = env.get_template('main.jinja2')
        return template.render(tou_text=text)

    def perform_action(self, action, request):
        if request.POST.get('accept', ''):
            return
        msg = 'you must accept'
        raise self.ActionError(msg)

    def get_tou_text(self, version):
        pass

def get_plugin():
    return ToUPlugin()
