from bson import ObjectId
from eduid_actions.testing import FunctionalTestCase


TOU_ACTION = {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('123467890123456789014567'),
        'action': 'tou',
        'preference': 100,
        'params': {
            'version': 'v1'
            }
        }


class ToUActionTests(FunctionalTestCase):

    def test_action_success(self):
        self.db.actions.insert(TOU_ACTION)
        # token verification is disabled in the setUp
        # method of FunctionalTestCase
        url = ('/?userid=123467890123456789014567'
                '&token=abc&nonce=sdf&ts=1401093117')
        res = self.testapp.get(url)
        self.assertEqual(res.status, '302 Found')
        res = self.testapp.get(res.location)
        form = res.forms['tou-form']
        self.assertEqual(self.db.actions.find({}).count(), 1)
        res = form.submit('accept')
        self.assertEqual(self.db.actions.find({}).count(), 0)
